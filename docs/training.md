# Training and local inference

The optional training package actually creates a small causal transformer from parameters and JSONL examples, or fine-tunes an explicitly approved local model. The desktop installer does not bundle PyTorch or download model weights. A tiny synthetic smoke run validates mechanics only; a few samples cannot produce a competent universal coding model.

## Data contract and sourcing

Each JSONL row has exactly `prompt`, `completion`, `project`, `license`. Use examples you own or selected rights-cleared permissive code with retained provenance. Sources can include your own reviewed project/test histories, official documentation/examples whose licenses permit the use, or individual datasets published with explicit licenses and consent. A public repository or a dataset listed on a hub is not blanket permission. Confirm redistribution/training terms, attribution, privacy and benchmark contamination yourself.

Review [Hugging Face dataset cards](https://huggingface.co/docs/hub/datasets-cards) for provenance/limitations and [The Stack's data governance](https://huggingface.co/datasets/bigcode/the-stack) before considering external code collections. This project does not download those collections or assert they meet your obligations. Prefer owned synthetic examples for pipeline tests. Never upload resumes, keys, customer code or private capstone data by default.

Preparation deduplicates normalized prompts, rejects conflicting completions, enforces an explicit license allowlist, hashes the data and assigns whole project groups to deterministic training/validation splits. At least two independent projects are needed. This prevents obvious row/project leakage, but near-duplicate/semantic leakage and hidden PII require additional review.

## Parameters and use

Install `.[training]` in a dedicated ML environment after reviewing hardware/storage needs. `examples/training.json` bounds architecture/context/steps/learning rate and selects CPU. For a new model, a byte-level BPE tokenizer is learned from training-only text and a GPT-2-style architecture is initialized from scratch. For fine-tuning, supply an approved local safe-tensor model and tokenizer directory; `trust_remote_code=False` and `local_files_only=True` prohibit implicit remote code/downloads.

```bash
python -m training.train --config examples/training.json --data examples/training.jsonl --output artifacts/new-model
# Configure STUDIO_MODEL_KEY privately with a strong 32+ character value.
python -m training.serve --model artifacts/new-model --port 11435
```

Model serving exposes a bounded authenticated loopback `/v1/chat/completions` endpoint. Configure an OpenAI-compatible studio provider with that URL and `STUDIO_MODEL_KEY`. A trained model must learn the required JSON proposal schema; arbitrary small-model output that fails validation is rejected, not turned into claimed working code. The application currently supports text generation models, not every possible architecture or custom agent protocol.

## Evaluation

Reports include parameter count, training loss series, held-out loss, split/hash/license metadata and caveats. Loss/perplexity is not compilation, pass@k, mutation strength, benchmark speed, security or code readability. Evaluate on independent unseen tasks with approved oracles, immutable tests, syntax checks, isolated execution, reproducible seeds, security review and measured provider cost/latency before using a model. Do not train on your evaluation answers. Saving a model and serving an API do not establish useful assistant quality.

