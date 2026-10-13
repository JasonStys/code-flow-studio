# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: main()@L22
# variables: temporary@L24; app@L25; client@L30; key@L38; language@L40; revision@L41; job@L44; deadline@L45; report@L47
# </code-map>

"""Jason Stys: genuine account API -> restricted Docker -> encrypted-history integration, run only in CI."""

import base64
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from examples.projects import fixture
from studio.models import LANGUAGES
from studio.private_api import create_private_app


def main():
    """Run every supported adapter through a real private session, then seal and reopen its actual reports."""
    with tempfile.TemporaryDirectory(prefix="code-flow-account-ci-") as temporary:
        app = create_private_app(Path(temporary) / "accounts", 8090)
        with TestClient(
            app,
            base_url="http://127.0.0.1:8090",
            headers={"X-CFS-Request": "v1", "Content-Type": "application/json"},
        ) as client:
            assert (
                client.post(
                    "/private/register",
                    json={"alias": "synthetic_ci", "password": "fictional-ci-long-password-2026"},
                ).status_code
                == 200
            )
            key = {"key": base64.b64encode(b"k" * 32).decode(), "salt": base64.b64encode(b"s" * 16).decode()}
            assert client.post("/private/unlock", json=key).status_code == 200
            for language in LANGUAGES:
                revision = client.post("/private/api/revisions", json=fixture(language).model_dump()).json()[
                    "id"
                ]
                job = client.post(f"/private/api/revisions/{revision}/run", json={}).json()["id"]
                deadline = time.monotonic() + 180
                while time.monotonic() < deadline:
                    report = client.get("/private/api/runs/" + job).json()
                    if report["status"] not in {"queued", "running"}:
                        break
                    time.sleep(0.25)
                assert report["status"] == "completed", (language, report)
                assert (
                    report["result"]["checks"]["passed"] == 1 and report["result"]["checks"]["failed"] == 0
                ), (language, report)
                print(language, "private compile/oracle passed", flush=True)
            assert client.post("/private/lock", json={}).status_code == 200
            assert not app.state.manager.active.exists()
            assert client.post("/private/unlock", json=key).status_code == 200
            assert len(client.get("/private/api/revisions").json()) == len(LANGUAGES)
            assert client.post("/private/lock", json={}).status_code == 200
            print("Encrypted real worker history reopened successfully", flush=True)


if __name__ == "__main__":
    main()
