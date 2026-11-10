# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: data_directory()@L27; parent_guard(server)@L40; main()@L61; shutdown()@L97; run_server()@L102
# variables: base@L32; base@L34; base@L36; pid@L42; started@L43; parent@L47; parser@L63; args@L68; bundle@L71; ui@L72; listener@L73; port@L76; app@L77; server@L84; thread@L111; deadline@L115; url@L120
# parameters: server@L40
# </code-map>

"""Jason Stys: token-free local account website and frozen service; never run submitted code on the host."""

import argparse
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import psutil
import uvicorn

from studio.native_lifecycle import native_stage
from studio.private_api import create_private_app


def data_directory() -> Path:
    """Return a new per-OS private root outside Git/installation and all legacy controller data."""
    if os.environ.get("CFS_ACCOUNT_DATA"):
        return Path(os.environ["CFS_ACCOUNT_DATA"])
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "CodeFlowStudioAccounts"


def parent_guard(server):
    """An exact native parent PID/create-time monitor requests graceful sealing if its launcher disappears."""
    pid = os.environ.get("CFS_PARENT_PID")
    started = os.environ.get("CFS_PARENT_STARTED")
    if not pid:
        return
    try:
        parent = psutil.Process(int(pid))
        if started and abs(parent.create_time() - float(started)) > 0.02:
            server.should_exit = True
            return
        while not server.should_exit:
            try:
                parent.wait(timeout=0.5)
                server.should_exit = True
            except psutil.TimeoutExpired:
                pass
    except (psutil.NoSuchProcess, ValueError):
        server.should_exit = True


def main():
    """Prebind literal loopback, start the private app, and print only a nonsecret website URL."""
    parser = argparse.ArgumentParser(description="Code Flow Studio - Jason Stys")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--ui", type=Path)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if args.port and not 1024 <= args.port <= 65535:
        raise SystemExit("Port must be automatic (0) or 1024..65535")
    bundle = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    ui = args.ui or (bundle / "ui" if getattr(sys, "frozen", False) else bundle / "dist" / "ui")
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", args.port))
    listener.listen(128)
    port = listener.getsockname()[1]
    app = create_private_app(
        args.data or data_directory(),
        port,
        ui,
        os.environ.get("CFS_LAUNCH_TOKEN", ""),
        os.environ.get("CFS_LAUNCH_NONCE", ""),
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            access_log=False,
            log_level="warning",
            proxy_headers=False,
            limit_concurrency=50,
            timeout_keep_alive=5,
        )
    )

    def shutdown():
        """Record actual accepted launcher shutdown before requesting the existing graceful server stop."""
        native_stage("shutdown-callback")
        server.should_exit = True

    def run_server():
        """Separate HTTP/lifespan completion from the frozen process/bootloader exit."""
        native_stage("server-thread-started")
        try:
            server.run(sockets=[listener])
        finally:
            native_stage("server-thread-stopped")

    app.state.shutdown = shutdown
    thread = threading.Thread(target=run_server, daemon=False)
    thread.start()
    threading.Thread(target=parent_guard, args=(server,), daemon=True).start()
    try:
        deadline = time.monotonic() + 30
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.started:
            raise SystemExit("Account service failed to start; preserve private recovery data")
        url = f"http://127.0.0.1:{port}/"
        print("Code Flow Studio - Jason Stys:", url, flush=True)
        print("Local only. Compiler jobs require an isolated local Docker engine.", flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        server.should_exit = True
        thread.join(timeout=30)
    finally:
        server.should_exit = True
        listener.close()
        native_stage("main-complete")


if __name__ == "__main__":
    main()
