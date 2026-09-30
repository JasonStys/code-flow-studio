"""Real causal-model training: new small model or local approved-model fine-tuning.

Symbol and variable locations: docs/code-index.md. Heavy ML dependencies are
optional. Training loss is not a code-correctness score; see docs/training.md.
"""

import argparse
import json
import math
from pathlib import Path

from training.dataset import prepare


def train(config: dict, data: Path, output: Path) -> dict:
    """Train explicitly sized CPU/GPU jobs; save tokenizer, weights, provenance and held-out loss."""
    import torch
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        GPT2Config,
        GPT2LMHeadModel,
        PreTrainedTokenizerFast,
    )

    allowed = {
        "mode",
        "seed",
        "steps",
        "learning_rate",
        "context",
        "layers",
        "hidden",
        "heads",
        "vocab_size",
        "base_model",
        "device",
    }
    if set(config) - allowed:
        raise ValueError("Unknown training parameters")
    seed = int(config.get("seed", 42))
    steps = int(config.get("steps", 20))
    context = int(config.get("context", 256))
    learning_rate = float(config.get("learning_rate", 0.0005))
    if (
        not 1 <= steps <= 10000
        or not 32 <= context <= 2048
        or not math.isfinite(learning_rate)
        or not 0 < learning_rate <= 0.01
    ):
        raise ValueError("Training budget out of bounds")
    training, validation, provenance = prepare(data, seed)
    torch.manual_seed(seed)
    text = [f"Task: {row['prompt']}\nResponse: {row['completion']}" for row in training]
    if config.get("mode", "new") == "new":
        layers, hidden, heads = (
            int(config.get(key, default)) for key, default in (("layers", 2), ("hidden", 64), ("heads", 2))
        )
        if not 1 <= layers <= 12 or not 32 <= hidden <= 1024 or not 1 <= heads <= 16 or hidden % heads:
            raise ValueError("Invalid bounded architecture")
        tokenizer_backend = Tokenizer(models.BPE(unk_token="[UNK]"))  # noqa: S106 -- tokenizer vocabulary, not a secret
        tokenizer_backend.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        tokenizer_backend.train_from_iterator(
            text,
            trainers.BpeTrainer(
                vocab_size=min(32768, max(256, int(config.get("vocab_size", 1024)))),
                special_tokens=["[UNK]", "[PAD]", "[EOS]"],
                initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
            ),
        )
        tokenizer = PreTrainedTokenizerFast(
            tokenizer_object=tokenizer_backend, unk_token="[UNK]", pad_token="[PAD]", eos_token="[EOS]"  # noqa: S106 -- vocabulary symbols, not credentials
        )
        model = GPT2LMHeadModel(
            GPT2Config(
                vocab_size=len(tokenizer),
                n_positions=context,
                n_ctx=context,
                n_embd=hidden,
                n_layer=layers,
                n_head=heads,
                bos_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
            )
        )
    elif config["mode"] == "finetune":
        base = Path(config["base_model"]).resolve()
        if not base.is_dir():
            raise ValueError("Supply an approved local model directory; no implicit model download")
        tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True, trust_remote_code=False)
        model = AutoModelForCausalLM.from_pretrained(
            base, local_files_only=True, trust_remote_code=False, use_safetensors=True
        )
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
    else:
        raise ValueError("Mode must be new or finetune")
    device = config.get("device", "cpu")
    if device not in {"cpu", "cuda"}:
        raise ValueError("Device must be cpu or cuda")
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    losses = []
    model.train()
    for step in range(steps):
        row = text[step % len(text)]
        batch = tokenizer(row, truncation=True, max_length=context, return_tensors="pt")
        batch = {key: value.to(device) for key, value in batch.items() if key != "token_type_ids"}
        labels = batch["input_ids"].clone()
        if labels.shape[1] < 2:
            raise ValueError("Training record tokenized too short")
        loss = model(**batch, labels=labels).loss
        if not torch.isfinite(loss):
            raise ValueError("Non-finite loss; training stopped")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1)
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
    model.eval()
    held_out = []
    with torch.no_grad():
        for row in validation:
            batch = tokenizer(
                f"Task: {row['prompt']}\nResponse: {row['completion']}",
                truncation=True,
                max_length=context,
                return_tensors="pt",
            )
            batch = {key: value.to(device) for key, value in batch.items() if key != "token_type_ids"}
            if batch["input_ids"].shape[1] >= 2:
                held_out.append(float(model(**batch, labels=batch["input_ids"]).loss.cpu()))
    output.mkdir(parents=True, exist_ok=False)
    model.save_pretrained(output, safe_serialization=True)
    tokenizer.save_pretrained(output)
    result = {
        "parameters": config,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "training_loss": losses,
        "held_out_loss": sum(held_out) / len(held_out) if held_out else None,
        "provenance": provenance,
        "caveat": "Small synthetic demonstration is not a useful general coding assistant. Validate generated code with independent tests before deployment.",
    }
    (output / "training-report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    """Run a reviewed parameter file and rights-cleared JSONL dataset into a new output directory."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(train(json.loads(args.config.read_text()), args.data, args.output), indent=2))


if __name__ == "__main__":
    main()
