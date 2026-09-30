# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_provider_protocols(tmp_path, project, monkeypatch, kind)@L24; handler(request)@L49; test_provider_endpoint_validation(tmp_path, url)@L84
# variables: path@L26; proposal@L44; captured@L47; body@L51; real_client@L60; router@L64; result@L65; path@L86
# parameters: kind@L24; monkeypatch@L24; project@L24; tmp_path@L24; request@L49; kwargs@L62; tmp_path@L84; url@L84
# </code-map>

"""Mocked protocol contracts, consent and response validation; not live AI quality tests.
Symbol and variable locations: docs/code-index.md.
"""

import asyncio
import json

import httpx
import pytest

from studio.models import AIRequest
from studio.providers import Providers


@pytest.mark.parametrize("kind", ["openai", "anthropic", "ollama"])
def test_provider_protocols(tmp_path, project, monkeypatch, kind):
    """Task routers validate JSON proposals and keep API keys in server headers only."""
    path = tmp_path / "providers.json"
    path.write_text(
        json.dumps(
            {
                "providers": [
                    {
                        "id": "test",
                        "kind": kind,
                        "url": "https://model.example/api",
                        "model": "contract-model",
                        "key_env": "STUDIO_TEST_KEY",
                    }
                ],
                "routes": {"improve": "test"},
            }
        )
    )
    monkeypatch.setenv("STUDIO_TEST_KEY", "private-test-key")
    proposal = json.dumps(
        {"explanation": "Example", "files": [], "tests": "", "suggestions": ["Review boundary cases"]}
    )
    captured = []

    def handler(request):
        captured.append(request)
        body = (
            {"choices": [{"message": {"content": proposal}}]}
            if kind == "openai"
            else {"content": [{"type": "text", "text": proposal}]}
            if kind == "anthropic"
            else {"message": {"content": proposal}}
        )
        return httpx.Response(200, json=body)

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs)
    )
    router = Providers(path)
    result = asyncio.run(router.request(AIRequest(task="improve", project=project, consent=True)))
    assert not result["verified"] and result["proposal"]["suggestions"]
    assert "private-test-key" not in captured[0].content.decode() and "private-test-key" not in json.dumps(
        router.public()
    )
    with pytest.raises(ValueError, match="consent"):
        asyncio.run(router.request(AIRequest(task="improve", project=project)))


@pytest.mark.parametrize(
    "url",
    [
        "http://remote.example/api",
        "https://user:password@model.example",
        "https://model.example?key=secret",
        "file:///tmp/model",
        "https://model.example#secret",
    ],
)
def test_provider_endpoint_validation(tmp_path, url):
    """Reject insecure or credential-bearing administrator endpoints."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"providers": [{"id": "bad", "kind": "openai", "model": "test", "url": url}]}))
    with pytest.raises(ValueError):
        Providers(path)
