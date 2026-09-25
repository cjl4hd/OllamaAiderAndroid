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
| `adb-ai` | Ubuntu (proot) | Wireless adb to the phone itself + Android memory tiers: kill hogs (Facebook/Instagram), phantom-killer off, revert; run `ubuntu` first |
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
11. Benchmark Model (model picker → decode + prefill probes → tok/s at 2
    decimals, plus the model's actual loaded RAM from Ollama's `/api/ps` —
    weights + KV cache at the active context; bench.py / bench_all.py remain
    the deep benchmarks)
12. Android Memory (adb-ai) — launches `adb-ai` inside Ubuntu: wireless adb to
    the phone, tiered Android memory reduction (Tier 0 info / 1 safe kills /
    2 persistent tuning incl. phantom-killer off / 3 root-gated, plus revert)
13. Quit

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
| `OLLAMA_NUM_PARALLEL` | `1` | Concurrent request slots. Ollama's default (4) multiplies KV-cache RAM 4x; keep at 1 on phones |
| `OLLAMA_KEEP_ALIVE` | `-1` | Keep the model loaded forever. Reloads cost minutes on a phone; set e.g. `30m` only if a big model squeezes RAM |
| `OLLAMA_LOAD_TIMEOUT` | `15m` | Max wait for a cold load. Ollama's default 5m is tight for phone flash + large GGUFs |
| `OLLAMA_KEEP_ALIVE` | `-1` | Keep the model loaded forever. Reloads cost minutes on a phone; set e.g. `30m` only if a big model squeezes RAM |
| `OLLAMA_LOAD_TIMEOUT` | `15m` | Max wait for a cold load. Ollama's default 5m is tight for phone flash + large GGUFs |

`adb-ai` has its own config, `~/.adb-ai.conf`, inside the **Ubuntu** home
(Termux's `~/.ai-env.conf` is not visible from the container), seeded on first
run: `KILL_PACKAGES` (tier-1 force-stop list, defaults include the Facebook
trio + Instagram), `MAX_CACHED_PROCESSES` (default 16),
`BACKGROUND_PROCESS_LIMIT` (default 2). State/backups: `~/.config/adb-ai/`.

### Choosing a model

The model picker serves both Aider and OpenCode. For OpenCode launches it gains
a **cloud** entry **after** the local models:

```
Installed models:
 1) qwen-coder-7b:latest ⭐
 2) gemma-4-E2B-it-Q4_K_M:latest
    -- cloud --
 4) ☁ OpenCode cloud (its default model)
```

- Pick a **local** model → OpenCode starts with `--model ollama/<name>` as before.
- Pick **cloud** → OpenCode starts bare, using its own default cloud model
  (no `--model` flag, no Ollama involvement). Useful when the phone's RAM is
  spoken for or you want a stronger model for a one-off task.
- The last choice is remembered and starred next launch; cloud being last keeps
  the Enter-default on your first local model.
- Only menu 7 (OpenCode) shows the cloud entry — Aider and chat stay local-only.

### Flags

- `update-ai -v / -q / -f / -h` — verbose, quiet, skip confirmation, help
- `clear-ai-cache -n / -f / -q / -h` — hide size report, skip prompts, quiet, help
  (default shows sizes and prompts for every destructive step; your last-used model
  is always kept)

## Android memory (`adb-ai`)

Run inside Ubuntu (`ubuntu`, then `adb-ai` — or just use `code` → 12). It pairs
wireless adb **to the phone the container runs on** (loopback) and frees Android
RAM — the same RAM Ollama/aider need:

```
adb-ai                  # pair once, connect, status
adb-ai mem              # tiered menu: 0 info / 1 kills / 2 persistent / 3 root / revert
adb-ai apps --top       # biggest Android memory consumers
adb-ai apps --frozen    # exactly what adb-ai froze (tracked, revertible)
adb-ai mem --t1         # kill list (Facebook, Instagram, …) + cached-process kill
adb-ai revert           # restore every Tier-2 original
```

- First pairing: on the phone open *Developer options → Wireless debugging →
  Pair device with pairing code* and **split the screen** (or float the app over
  Settings) — the pairing port closes the instant the dialog is dismissed.
- Tier 2 disables Android 12+'s **phantom process killer** (the thing that
  reaps Termux/proot children mid-run) and saves every original; `adb-ai
  revert` restores them.
- Config: `~/.adb-ai.conf` inside the Ubuntu home (kill list, caps).
- Freezes are tracked: `apps --freeze` records every package **we** disabled
  (pre-disabled bloat is never tracked) in `~/.config/adb-ai/frozen.txt`;
  `apps --frozen` lists them, `apps --unfreeze PKG` / `--unfreeze-all` undo —
  so undo inverts exactly our actions.
- Device-verified result on a 12 GB S26: MemAvailable 2.4 → 5.1 GB, zram swap
  100% → 50% after Tier 1.

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

- **adb-ai — fully device-verified on SM-S942U1 (S26)**: pairing, connect,
  Tier 0 (Samsung dumpsys format parsed), Tier 1 (MemAvailable 2.4→5.1 GB,
  zram 100%→50%), Tier 2 (phantom killer off, verified via device_config get;
  backups + revert path written), Tier 3 error path (no root), status. Also
  proved: an adb client in proot must not hold the caller's stdout pipe (redirect
  to files + `timeout -k`), and Samsung's meminfo section is `380,893K: pkg`.

Paths proven in review (logic verified, syntax-checked, config output
JSON-validated) but **not yet run on device**:

- **nvm PATH detection fix — device-verified**: opencode/freebuff installed via
  nvm-installed npm (`~/.nvm/versions/node/*/bin`) were invisible to `bash -lc`
  detection; scripts now resolve via explicit candidate paths
  (`ubuntu_which` / `in_ubuntu_path`) and launch by **absolute path**.
- **PATH export removed from launchers — device-bisected**: exporting the
  nvm/.local PATH prefix inside the launch string wedged opencode's TUI
  startup (bisect: cd+opencode renders, PATH-export+opencode hangs). Launchers
  now use plain `cd + absolute-path binary`. `update-ai` keeps the export for
  its non-interactive commands, where it works fine.
- **Launch-string fix — device-verified root cause**: the first launch attempt
  failed with `syntax error near unexpected token '}'` because the PATH prefix
  (`export PATH=...`) was joined to the binary with a brace group that bash
  cannot parse mid-command. Now joined with `&&`. Old form's failure reproduced
  and new form's parse + exec verified in a stubbed harness; full on-device
  launch still to confirm.
- Freebuff install/update path in `update-ai` (assumes `apt install nodejs npm`
  works in proot Ubuntu; not yet exercised)
- Freebuff launch from `code` — first on-device attempt hit the npm-shim
  shebang problem (`env: 'node': No such file or directory`); launcher fixed
  to run the shim via node's absolute path (same lesson as the opencode
  launch). Full first launch still to exercise.
- **OpenCode local-model flow — mostly device-verified**: config generation
  (with the schema-required `limit.output`, capped at 4096), Ollama's
  OpenAI-compatible `/v1` endpoint, and a full `opencode run "say hi" --model
  ollama/<model>` turn all confirmed on device. Memory findings: Ollama's
  default `num_parallel=4` quadruples KV-cache RAM and alone can keep a 7b
  model from loading on a 12 GB phone — `OLLAMA_NUM_PARALLEL=1` is now the
  default (restart `code` or `restart_ollama` to apply); gemma-E2B loads in
  ~5 min even so. **The TUI is device-verified**: renders and stays responsive
  with `--model ollama/...`. Remaining issue: very slow model responses —
  tracked in Todo. First suspect: that session ran before Ollama was restarted
  with `OLLAMA_NUM_PARALLEL=1`, so the 4-slot KV-cache tax was still active.
- `add_models.sh` (filenames confirmed against `/storage/emulated/0/Models/`;
  script itself unrun)
- Status banner `Loaded`/`Ctx` lines and menu options 9–10

If a fresh `update-ai` run on another phone stalls at the OpenCode/Freebuff
prompts, that's the new ask-based install flow — `-f` skips prompts.

## Todo

- Verify setup / update / run scripts on another phone
- Debug slow Ollama responses in OpenCode (TUI itself verified: renders, responsive):
  1. Retest after restarting Ollama with `OLLAMA_NUM_PARALLEL=1` — the first
     slow session ran under the old server (num_parallel=4 KV-cache tax, and
     possibly a partially-loaded model). This alone may close it.
  2. Measure: menu 11 (Benchmark Model) gives whole-run tok/s per model;
     `bench.py`/`bench_all.py` give the prompt-eval vs decode split. If decode
     is fine but responses stay slow, compare aider (native `/api`) vs opencode
     (`/v1`) latency to isolate endpoint overhead, and watch for thermal
     throttling on sustained generation (thread count is a per-request
     `num_thread` Modelfile option — there is no `OLLAMA_NUM_THREAD` env var).
  3. Physics note: OpenCode's agent loop sends a large prompt (system + tools +
     session context) every turn — prefilling thousands of tokens is inherently
     slow at phone compute speeds. Some of this is cost-of-doing-business, not
     a bug; judge by tokens/sec, not wall-clock first response.
- Verify Freebuff on-device install/update path in `update-ai` (launch now
  works via node absolute path; the update-ai install steps have not been
  re-exercised since)
- Add support for optional plugins/tools:
  - whisper
  - kiwix
  - ssh
