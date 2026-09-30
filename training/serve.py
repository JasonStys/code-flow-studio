"""Authenticated loopback OpenAI-compatible API for locally trained safe-tensor models.

Symbol and variable locations: docs/code-index.md. Serving is separate from
compiler workers and remains untrusted AI generation, not a correctness oracle.
"""

import argparse
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field


def create_model_api(directory: Path, token: str) -> FastAPI:
    """Load a local, explicitly approved model with no remote-code execution or downloads."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if len(token) < 32:
        raise ValueError("Use a strong private model API token")
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        directory, local_files_only=True, trust_remote_code=False, use_safetensors=True
    ).eval()
    app = FastAPI(docs_url=None, redoc_url=None)

    class Completion(BaseModel):
        """Bound request size; the coding studio still validates the generated proposal schema."""

        model_config = ConfigDict(extra="ignore")
        messages: list[dict[str, str]] = Field(min_length=1, max_length=20)
        max_tokens: int = Field(default=128, ge=1, le=512)

    @app.post("/v1/chat/completions")
    def complete(request: Completion, authorization: str = Header(default="")):
        """Generate a bounded completion; never execute it or imply validation."""
        if not secrets.compare_digest(authorization, "Bearer " + token):
            raise HTTPException(401, "Authentication required")
        text = "\n".join(message.get("content", "") for message in request.messages)
        if len(text) > 96000:
            raise HTTPException(413, "Context too large")
        context = model.config.max_position_embeddings
        budget = min(request.max_tokens, context // 2)
        batch = tokenizer(text, return_tensors="pt", truncation=True, max_length=context - budget)
        batch.pop("token_type_ids", None)
        with torch.no_grad():
            generated = model.generate(
                **batch, max_new_tokens=budget, do_sample=False, pad_token_id=tokenizer.pad_token_id
            )
        result = tokenizer.decode(generated[0][batch["input_ids"].shape[1] :], skip_special_tokens=True)
        return {"choices": [{"message": {"role": "assistant", "content": result}}], "verified": False}

    return app


def main() -> None:
    """Serve a local model with a separately configured token, never an anonymous public endpoint."""
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--port", type=int, default=11435)
    args = parser.parse_args()
    token = os.environ.get("STUDIO_MODEL_KEY", "")
    uvicorn.run(create_model_api(args.model, token), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
