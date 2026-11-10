# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: completed_offload(function)@L24; completed_operation(operation)@L38; capture()@L45
# variables: work@L52; cancelled@L53; result@L56; succeeded@L56; cancelled@L63
# parameters: args@L24; function@L24; kwargs@L24; operation@L38
# </code-map>

"""Jason Stys: complete owned blocking work before propagating HTTP-task cancellation.

Symbol locations: docs/code-index.md. Never release a surrounding vault/request
mutex while its worker can still read or replace the protected filesystem state.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import cast

from starlette.concurrency import run_in_threadpool

from studio.native_lifecycle import native_stage


async def completed_offload[**P, T](function: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Defer even repeated outer Task.cancel until the real owned thread operation finishes.

    Starlette/AnyIO's default cancel scope does not protect against raw asyncio
    Task.cancel. A separately retained shielded task keeps the caller inside its
    existing mutex. Worker errors are transported as data to avoid Python 3.14
    shield logging a child failure after outer cancellation; the sole caller
    then receives the actual error or the original cancellation with its cause.
    This helper never cancels its child or uses a timeout to abandon disk work.
    """

    return await completed_operation(run_in_threadpool(function, *args, **kwargs))


async def completed_operation[T](operation: Awaitable[T]) -> T:
    """Finish one bounded owned state transition before propagating outer cancellation.

    Use only for disk work or coherent workspace transitions, never an unbounded
    network request/body. The surrounding caller retains its existing mutex.
    """

    async def capture() -> tuple[bool, T | Exception]:
        """Return ordinary errors as data for the sole awaiting task, without shield child-error logging."""
        try:
            return True, await operation
        except Exception as error:
            return False, error

    work = asyncio.create_task(capture())
    cancelled = None
    while True:
        try:
            succeeded, result = await asyncio.shield(work)
            break
        except asyncio.CancelledError as error:
            if work.cancelled():
                raise RuntimeError("Owned offload was independently cancelled") from error
            if cancelled is None:
                native_stage("offload-cancellation-deferred")
            cancelled = cancelled or error
        except BaseException as error:
            if cancelled is not None:
                raise cancelled from error
            raise
    if cancelled is not None:
        if not succeeded:
            raise cancelled from cast(Exception, result)
        raise cancelled
    if not succeeded:
        raise cast(Exception, result)
    return cast(T, result)
