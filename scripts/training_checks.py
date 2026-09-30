"""Actual trained-model API smoke, explicitly not a code-quality benchmark.
Symbol and variable locations: docs/code-index.md.
"""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from training.serve import create_model_api


def main():
    """Check private model API auth and generation using the just-trained tiny fixture."""
    key = "model-test-only-" + "x" * 32
    app = create_model_api(Path("artifacts/model"), key)
    with TestClient(app) as client:
        body = {
            "messages": [{"role": "user", "content": "Task: Explain branch coverage.\nResponse:"}],
            "max_tokens": 8,
        }
        assert client.post("/v1/chat/completions", json=body).status_code == 401
        response = client.post("/v1/chat/completions", json=body, headers={"Authorization": "Bearer " + key})
        assert response.status_code == 200, response.text
        assert isinstance(response.json()["choices"][0]["message"]["content"], str)
        result = {
            "api_auth_verified": True,
            "real_model_completion": response.json(),
            "caveat": "Pipeline smoke only; tiny model output is not useful or verified code",
        }
    Path("artifacts/model/api-smoke.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
