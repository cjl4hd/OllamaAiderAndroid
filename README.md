# Android AI Development Environment

A set of scripts to install and run a full AI coding environment on an Android phone:
Ollama on Termux (host), plus Aider and OpenCode inside a proot-distro Ubuntu
container — all on-device, no cloud required.

## Setup

```bash
mkdir -p projects        # or cd into an existing project directory
git clone git@github.com:cjl4hd/OllamaAiderAndroid.git
cd OllamaAiderAndroid
update-ai
code
```

`update-ai` runs non-interactively-safe first-time setup: installs proot Ubuntu,
Python 3.12 + Aider (via uv), Ollama, optionally OpenCode, and links everything
into Termux's bin.

## Hardware

- Samsung Galaxy S26 (Snapdragon)
- Android
- Termux
- Ubuntu (proot-distro)

## Architecture

```
Android
└── Termux (host)
    ├── Ollama            ← tuned per phone: flash attention, q8_0 KV cache,
    │                       1 loaded model at a time (set in `code`)
    └── proot-distro
        └── Ubuntu
            ├── Aider      ← repo-map editing, git-integrated
            ├── OpenCode   ← agentic editor (optional, via update-ai)
            └── projects (git)
```

## Important Commands

| Command | Runs | What it does |
|---|---|---|
| `code` | Termux | Interactive launcher — model/project picker + menu (below) |
| `update-ai` | Termux | Install/update everything; creates `~/.ai-env.conf` |
| `doctor-ai` | Termux | Health checks: installs, server, API reachability, versions |
| `clear-ai-cache` | Termux | Tiered cache cleanup (Tier 1 safe / Tier 2 destructive) |
| `ubuntu` | Termux | Shell into the Ubuntu container |
| `aider-ubuntu` | Termux | Run aider with args, e.g. `aider-ubuntu --model qwen --chat-mode ask` |
| `add_models.sh` | Termux | One-shot `ollama create` for the Modelfiles in this repo |
| `uv_aider_install.sh` | Ubuntu | Manual fallback install of uv + Python 3.12 + aider-chat |
| `bench.py` | Termux | Per-model llama.cpp benchmark → `benchmark.csv` |
| `bench_all.py` | Termux | Benchmark every GGUF in the models dir → CSV + `leaderboard.md` |

### `code` menu

1. Launch Aider (model picker → project picker → aider inside Ubuntu)
2. Import GGUF (pick a `.gguf` from the models dir, name it, `ollama create`)
3. Chat (`ollama run` with the chosen model)
4. Update AI (delegates to `update-ai`)
5. Doctor AI (delegates to `doctor-ai`)
6. Restart Ollama
7. OpenCode (project picker → opencode inside Ubuntu; generates an Ollama
   provider config on first run so installed Ollama models are selectable)
8. Clear Cache (delegates to `clear-ai-cache`)
9. Freebuff (project picker → freebuff inside Ubuntu; cloud models, no API key)
10. Regen OpenCode Config (overwrite the generated `opencode.json` from the
    current `ollama list` — use after importing a new model)
11. Quit

## Configuration

`~/.ai-env.conf` is created by `update-ai` and sourced by `code`, `update-ai`,
`doctor-ai`, and `clear-ai-cache`:

| Key | Default | Purpose |
|---|---|---|
| `PYTHON_VERSION` | `3.12` | Python version for uv / aider-chat |
| `UBUNTU_DISTRO_NAME` | `ubuntu` | proot-distro container name |
| `PROJECT_NAME` | `OllamaAiderAndroid` | Git project directory name |
| `PROJECT_DIR` | *(auto-detected)* | Absolute path override if the clone lives elsewhere |
| `GGUF_DIR` | `/storage/emulated/0/Models` | Where `.gguf` model files are imported from |
| `OPENCODE` | `ask` | `ask` (prompt if missing) or `no` (never install) |
| `FREEBUFF` | `ask` | `ask` (prompt if missing) or `no` (never install) |
| `OLLAMA_CONTEXT_LENGTH` | `16384` | Ollama default context window. OpenCode wants 64k+; lower if RAM-constrained |

### Flags

- `update-ai -v / -q / -f / -h` — verbose, quiet, skip confirmation, help
- `clear-ai-cache -n / -f / -q / -h` — hide size report, skip prompts, quiet, help
  (default shows sizes and prompts for every destructive step; your last-used model
  is always kept)

## Models

Android storage:

```
/storage/emulated/0/Models/
```

Imported into Ollama using a Modelfile:

```
FROM /data/data/com.termux/files/home/storage/shared/Models/qwen2.5-coder-7b-instruct-q4_k_m.gguf
```

This lets you download models on your phone and point to them from Termux/Ubuntu.
The `Models` directory lives in the Android home directory, separate from
Downloads. Files are imported into Ollama for management — you can delete them
from the models directory once imported.

Create:

```bash
ollama create qwen-coder-7b -f Modelfile
```

Or use `code` → 2) Import GGUF, which prompts for the file and name.

## Start Coding

```bash
code
```

This command lets you choose your AI model and project, then runs the Ollama
server and Aider (or OpenCode) in the project directory.

## Notes

Projects are stored in proot Ubuntu:

```
~/projects        (inside Ubuntu: /root/projects)
```

Cross-mounted for convenience (created by `update-ai`):

- Termux home ↔ Ubuntu home (`ubuntu-home` / `termux-home` symlinks)
- Android storage (`android-home` in both)

Models remain in:

```
~/storage/shared/Models
```

## For AI agents

- `AGENTS.md` — project map and hard rules for coding agents (agents.md
  convention; `CLAUDE.md` points to it)
- `.agents/skills/small-model-context/` — loadable skill with context-economy
  rules for 7B-class local models
- `.aider.conventions.md` — aider's auto-loaded prompt guard

## Using OpenCode with a local model

1. `code` → pick model → **7) OpenCode** → pick project. The launcher generates
   `~/.config/opencode/opencode.json` inside Ubuntu (Ollama provider, all
   installed models) and starts OpenCode with your model preselected
   (`--model ollama/<name>`).
2. The provider talks to `http://127.0.0.1:11434/v1` — same loopback, since proot
   shares Android's network stack. Verify with `ollama ps` in a second Termux
   session while OpenCode generates.
3. **Gotcha:** the generated config is never auto-overwritten. After importing a
   new model, run `code` → **10) Regen OpenCode Config** (or delete
   `~/ubuntu-home/.config/opencode/opencode.json`).

In-app basics: `/init` once per project (writes `AGENTS.md`), `/models` to switch,
`/compact` to reclaim context, `/new` for a fresh session, `Esc` to interrupt.
At the default 16k context, `/compact` early — one file read plus conversation
fills it fast. First edit/command triggers a permission prompt; choose
allow-always for trusted projects.

## Live-testing notes

Paths proven in review (logic verified, syntax-checked, config output
JSON-validated) but **not yet run on device**:

- **nvm PATH detection fix — device-verified**: opencode/freebuff installed via
  nvm-installed npm (`~/.nvm/versions/node/*/bin`) were invisible to `bash -lc`
  detection; scripts now resolve via explicit candidate paths
  (`ubuntu_which` / `in_ubuntu_path`). Detection confirmed working on device.
- **Launch-string fix — device-verified root cause**: the first launch attempt
  failed with `syntax error near unexpected token '}'` because the PATH prefix
  (`export PATH=...`) was joined to the binary with a brace group that bash
  cannot parse mid-command. Now joined with `&&`. Old form's failure reproduced
  and new form's parse + exec verified in a stubbed harness; full on-device
  launch still to confirm.
- Freebuff install/update path in `update-ai` (assumes `apt install nodejs npm`
  works in proot Ubuntu; not yet exercised)
- Freebuff launch from `code` (never launched on device)
- OpenCode launch: model picker, config generation, and launch call all
  device-verified. Device testing caught a real bug: the generated config was
  rejected by OpenCode's schema (`Missing key ...limit.output`) and the TUI died
  silently on startup, which looked like a hang. The generator now emits
  `limit.output` (capped at 4096) for every model. **After updating, regenerate
  the cached config**: `code` → 10) Regen OpenCode Config → y. End-to-end agent
  session still to confirm.
- `add_models.sh` (filenames confirmed against `/storage/emulated/0/Models/`;
  script itself unrun)
- Status banner `Loaded`/`Ctx` lines and menu options 9–10

If a fresh `update-ai` run on another phone stalls at the OpenCode/Freebuff
prompts, that's the new ask-based install flow — `-f` skips prompts.

## Todo

- Verify setup / update / run scripts on another phone
- Fully support OpenCode in `code` and `update-ai` (model/provider config, doctor-ai coverage, menu parity with Aider)
- Add Freebuff agent support in `code` and `update-ai` at parity with OpenCode
- Add support for optional plugins/tools:
  - whisper
  - kiwix
  - ssh
