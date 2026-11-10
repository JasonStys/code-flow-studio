# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_native_cancellation_cannot_release_mutex_before_actual_worker(cancels, fail)@L24; offload_scenario(cancels, fail)@L29; worker()@L38; caller()@L48
# variables: release@L31; started@L31; mutex@L32; events@L33; unhandled@L33; loop@L34; original_handler@L35; request@L56; _@L59; outcome@L68
# parameters: cancels@L24; fail@L24; cancels@L29; fail@L29; _loop@L36; context@L36
# </code-map>

"""Jason Stys: actual thread completion under raw repeated asyncio cancellation.

Symbol locations: docs/code-index.md. All operations are disposable synchronized
fixtures, not account files, mocked threadpool completion or arbitrary-code execution.
"""

import asyncio
import threading

import pytest

from studio.completed_offload import completed_offload


@pytest.mark.parametrize("cancels,fail", [(0, False), (1, False), (2, False), (2, True), (0, True)])
def test_native_cancellation_cannot_release_mutex_before_actual_worker(cancels, fail):
    """Preserve successful results/errors and finish real work before cancellation and lock release."""
    asyncio.run(offload_scenario(cancels, fail))


async def offload_scenario(cancels, fail):
    """Order real worker completion before caller finally, even after repeated raw cancellation."""
    started, release = threading.Event(), threading.Event()
    mutex = asyncio.Lock()
    events, unhandled = [], []
    loop = asyncio.get_running_loop()
    original_handler = loop.get_exception_handler()
    loop.set_exception_handler(lambda _loop, context: unhandled.append(context))

    def worker():
        """Wait for a controlled release, then produce an actual result or ordinary worker error."""
        started.set()
        if not release.wait(5):
            raise AssertionError("Test did not release its worker")
        events.append("worker-finished")
        if fail:
            raise ValueError("fictional-worker-error")
        return 42

    async def caller():
        """Represent a vault operation whose surrounding lock must remain held until real I/O finishes."""
        try:
            async with mutex:
                return await completed_offload(worker)
        finally:
            events.append("caller-finally")

    request = asyncio.create_task(caller())
    try:
        assert await asyncio.to_thread(started.wait, 3)
        for _ in range(cancels):
            assert request.cancel()
            # Give actual CancelledError/shield callbacks their event-loop turns;
            # this is neither a duration-based wait nor worker cancellation.
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            assert mutex.locked() and not request.done() and events == []
        release.set()
        if cancels:
            with pytest.raises(asyncio.CancelledError) as outcome:
                await request
            assert not fail or isinstance(outcome.value.__cause__, ValueError)
        elif fail:
            with pytest.raises(ValueError, match="fictional-worker-error"):
                await request
        else:
            assert await request == 42
        assert events == ["worker-finished", "caller-finally"]
        assert not mutex.locked() and not unhandled
    finally:
        release.set()
        if not request.done():
            request.cancel()
            with pytest.raises(asyncio.CancelledError):
                await request
        loop.set_exception_handler(original_handler)
