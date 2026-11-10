# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: NativeServer@L34
# functions: native_config(app, port)@L25; shutdown(self, sockets)@L37; stage(self, name)@L43; _wait_tasks_to_complete(self)@L51
# variables: HTTP_DRAIN_SECONDS@L22; pending@L63; task@L63; task@L64
# parameters: app@L25; port@L25; self@L37; sockets@L37; name@L43; self@L43; self@L51
# </code-map>

"""Jason Stys: finite HTTP drain followed by completed request cleanup and normal vault sealing.

Symbol locations: docs/code-index.md. Pinned Uvicorn owns sockets and lifespan;
this subclass only joins its own canceled HTTP tasks before the lifespan can close.
"""

import asyncio

import uvicorn

from studio.native_lifecycle import native_stage

HTTP_DRAIN_SECONDS = 5.0


def native_config(app, port: int) -> uvicorn.Config:
    """Use identical literal-loopback and bounded-concurrency configuration in the shipping app and real tests."""
    return uvicorn.Config(
        app, host="127.0.0.1", port=port, access_log=False, log_level="warning",
        proxy_headers=False, limit_concurrency=50, timeout_keep_alive=5,
        timeout_graceful_shutdown=HTTP_DRAIN_SECONDS,
    )


class NativeServer(uvicorn.Server):
    """Bound idle/held HTTP work without abandoning active account filesystem operations."""

    async def shutdown(self, sockets=None):
        """Keep Uvicorn's normal listener/connection/lifespan cleanup, with value-free stage counts."""
        self.stage("http-drain-started")
        await super().shutdown(sockets=sockets)
        self.stage("http-drain-complete")

    def stage(self, name):
        """Observe counts only; no request routes, account data, source or authentication values."""
        native_stage(
            name,
            connections=len(self.server_state.connections),
            tasks=len(self.server_state.tasks),
        )

    async def _wait_tasks_to_complete(self):
        """On the configured drain timeout, finish cancellation cleanup before normal lifespan sealing.

        Uvicorn 0.38 otherwise cancels HTTP tasks and immediately starts lifespan
        shutdown. Joining those exact tasks lets protected offloads finish while
        their request locks are still held. Disk operations retain data safety over
        a fabricated fixed process-exit guarantee; no task is killed or detached.
        """
        try:
            await super()._wait_tasks_to_complete()
        except asyncio.CancelledError:
            self.stage("http-drain-budget-exhausted")
            pending = tuple(task for task in self.server_state.tasks if not task.done())
            for task in pending:
                task.cancel("Native HTTP drain deadline reached; complete owned cleanup")
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            self.stage("http-request-cleanup-complete")
            raise
