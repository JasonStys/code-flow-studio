# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Completion@L38
# functions: create_model_api(directory, token)@L25; complete(request, authorization)@L46; main()@L67
# variables: tokenizer@L32; model@L33; app@L36; model_config@L41; messages@L42; max_tokens@L43; message@L50; text@L50; context@L53; budget@L54; batch@L55; generated@L58; result@L61; parser@L71; args@L74; token@L75
# parameters: directory@L25; token@L25; authorization@L46; request@L46
# </code-map>

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
        max_tokens: int = Field(default=128, ge=1, le=8192)

    @app.post("/v1/chat/completions")
    def complete(request: Completion, authorization: str = Header(default="")):
        """Generate a bounded completion; never execute it or imply validation."""
        if not secrets.compare_digest(authorization, "Bearer " + token):
            raise HTTPException(401, "Authentication required")
        text = "\n".join(message.get("content", "") for message in request.messages)
        if len(text) > 96000:
            raise HTTPException(413, "Context too large")
        context = model.config.max_position_embeddings
        budget = min(request.max_tokens, context // 2, 512)
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
