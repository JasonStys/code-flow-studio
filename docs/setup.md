# Setup and operation

**Current installed/account mode:** follow [private-account setup](private-accounts.md) and use checksummed Releases. Source website command is `python -m studio.private_cli`; it prints a token-free loopback URL. The older token/config instructions below are only for explicit legacy developer/CI mode. No automatic legacy-data migration is performed.

## Packaged users

Windows: launch the single `Code Flow Studio Setup … .exe` artifact. It installs for the current user, retains history on uninstall, and bundles Electron, editor assets and the frozen service. No IntelliJ or separately installed Python is required. Development installers are unsigned and may prompt OS warnings; do not describe them as notarized/signed releases.

Linux uses an AppImage; macOS uses a DMG. Native packages are architecture/OS specific. Mobile devices use the responsive browser interface; native Android/iOS packaging is not implemented.

Execution prerequisites are separate from UI installation: Docker must be running, and the trusted `code-flow-worker:0.1.0` image must exist. Build the image from the reviewed `runner` directory. This can download compilers and libraries during trusted image installation; target jobs have no network. If unavailable, the UI remains usable but execution is explicitly blocked.

## Source developers

Use Python 3.12+ and Node 24. Install `.[dev]` into a private virtual environment, run `npm ci`, `npm run build`, then `python -m studio.cli serve`. The command prints a local fragment-token URL. Keep that token private. It is removed from the browser address after being placed in session storage. API endpoints require an Authorization header.

```bash
python -m venv .venv
# Activate the environment for your shell, then:
pip install -e '.[dev]'
npm ci
npm run build
docker build -t code-flow-worker:0.1.0 runner
python -m studio.cli serve --port 8012
```

For packaging, freeze `scripts/frozen_entry.py` as `code-flow-service` in `release/service`, then run `npm run package -- --publish never`. The workflow builds each OS on that OS and performs a native startup smoke check.

## AI setup

Copy `config/providers.example.json` to a private location outside Git. Set installed/model-accessible names and explicit task routes. Put keys in the named server environment variables. Launch source mode with `--config PATH`; packaged mode reads `providers.json` in its Electron user-data directory. Restart after changing routing. No key is entered through the renderer or stored in the repository.

Ollama requires a separately installed local model. OpenAI-compatible and Anthropic endpoints require privately configured keys. The application never downloads a model or makes paid calls automatically. Users consent before transmitting source. Live suggestions debounce edits but can still incur provider usage/cost; disabling consent disables live requests.

## CI usage

`python -m studio.cli analyze --project FILE --output artifacts` uses the exact same broker. An optional `code-flow.project.json` selects push inputs. `scripts/push_analysis.py` runs a baseline; an explicitly configured `STUDIO_PROVIDER_CONFIG` enables test/improvement generation and candidate retesting. AI execution should be push/manual-only, with read-only checkout and no secrets in fork PRs. Retained candidate artifacts require review; no automatic commits or merges occur.

The supplied Actions workflow has an explicit opt-in: add the repository variable `CODE_FLOW_ENABLE_AI=true`, the `STUDIO_AI_CONFIG` secret containing your reviewed provider JSON, and the separately named `STUDIO_OPENAI_KEY` and/or `STUDIO_ANTHROPIC_KEY` secrets. Configuration routes must reference those key environment names. AI credentials are provided only on main-branch push/manual runs, never pull-request runs. Leave the opt-in unset to avoid paid calls. Hosted GitHub runners cannot reach an Ollama instance on your PC; use an authorized HTTPS provider for CI. Configure secrets yourself through GitHub; do not paste them into chat, source, workflow YAML or reports.

Exports include bounded revision timelines (latest 50 revisions, latest ten attempts each), hashes, priorities and measurement summaries. Full source/logs are in each individual run export. Appending tests retains earlier test text, but cannot prove a malicious appended harness has not overridden behavior; independent approved cases and human review remain necessary.

## Diagnostics and recovery

“Docker unavailable” is not a code failure and is not a passed test. A missing image is a separate setup issue. Interrupted controller jobs become `interrupted` after restart. Stop the controller before moving/backing up the entire app data directory including SQLite/WAL companions. Do not reset Docker or delete existing containers/images to troubleshoot this application without explicit approval.

