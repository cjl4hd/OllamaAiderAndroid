# Working on OllamaAiderAndroid (agent guide)

Read this before making changes. Follows the [AGENTS.md](https://agents.md) convention
so any coding agent picks it up; `CLAUDE.md` just points here.

## What this is

Installer and launcher scripts for an on-device AI coding environment: Termux (host)
runs Ollama, a proot-distro Ubuntu container runs Aider and OpenCode, helper scripts
tie them together. The audience is a phone with limited RAM and storage — assume
nothing about the host beyond Termux + Android storage access.

## Project map

- `update-ai` — the installer/updater. Runs in Termux host only. Creates
  `~/.ai-env.conf`, installs/updates Ubuntu proot, Python/uv/Aider (in Ubuntu),
  Ollama (host), OpenCode (in Ubuntu, optional), storage symlinks, bin links.
- `code` — interactive launcher. Model picker, project picker, GGUF import, chat,
  delegates to update-ai / doctor-ai / clear-ai-cache. Sets Ollama env tuning
  (flash attention, q8_0 KV cache, single loaded model) for phone-class hardware.
- `doctor-ai` — health checks and version report.
- `clear-ai-cache` — tiered cache cleanup (Tier 1 safe / Tier 2 destructive, each
  prompted). Detects nested proot via parent-process walk.
- `ubuntu` — plain shell into the Ubuntu container (`proot-distro login`).
- `aider-ubuntu` — runs aider inside Ubuntu with argument passthrough via the
  `bash -lc 'aider "$@"' bash "$@"` trick. `aider-ubuntu.txt` is a tutorial
  explaining that trick — keep it in sync if the wrapper changes.
- `add_models.sh` — one-shot `ollama create` calls for the repo's Modelfiles.
- `uv_aider_install.sh` — manual fallback for the uv + Python + aider install.
- `bench.py`, `bench_all.py` — llama.cpp benchmarks (require `llama-cli` /
  `llama-bench` on PATH, not Ollama): per-prompt tok/s + peak RSS → CSV;
  bench_all also writes a `leaderboard.md` ranked by decode tok/s.
- `android_home` — committed symlink to `/storage/emulated/0/`.
- `termux_home/` — snapshot of the Termux/Ubuntu home layout (dotfiles, nested
  project copies). Reference material, not executed from here.

## Hard rules

1. **Host vs container matters.** `update-ai` and package installs run in Termux
   (host); Aider/OpenCode live inside proot Ubuntu. Never mix them: guard with the
   `/data/data/com.termux` check, and reach into Ubuntu only via
   `proot-distro login ... -- bash -lc`.
2. **Everything is user-configurable through `~/.ai-env.conf`.** Distro name,
   Python version, project dir, GGUF dir — source it, apply defaults with
   `:-`, never hardcode paths. New tunables go in the config file and the
   `update-ai` usage text together.
3. **Shebang must be `/data/data/com.termux/files/usr/bin/bash`** for scripts
   invoked as bare commands in Termux. (`update-ai` uses `/usr/bin/env bash`
   because it may run before the bin links exist — keep that distinction.)
4. **Prompts are the interface.** Scripts run interactively on first setup; every
   destructive step needs a confirm prompt, and every prompt needs a non-interactive
   escape (`--force`/`--quiet` flags). Don't add a blocking `read -p` without a
   skip path.
5. **Idempotent.** `update-ai` must be safe to re-run: check-before-install,
   upgrade-not-reinstall, warnings-not-deaths for things that may legitimately not
   exist on a first run.
5b. **Wrappers stay thin.** `ubuntu` and `aider-ubuntu` are one-liners on purpose;
   any argument-passing change to `aider-ubuntu` gets mirrored in
   `aider-ubuntu.txt` (it teaches the exact command structure).
6. **POSIX-safe bash, no dependencies beyond Termux + proot Ubuntu.** `set -e`
   (or `set -euo pipefail` where flags are parsed), quote everything, no jq/yq or
   other tools not installed by the scripts themselves.
7. **Docs ship with the change.** New command, flag, config key, or `code` menu
   option → update README (command table, menu list, config table) and the
   `usage()` text in the same change. Scripts are the docs' source of truth; docs
   that name a command the repo doesn't ship are worse than no docs.
8. **Review what you publish.** `termux_home/` contains snapshots of real home
   directories. Before committing: `git status --short`, stage by explicit path,
   never `git add -A`. No credentials, tokens, chat history, or device-identifying
   paths in anything committed (check `termux_home/**/.config/**` and history files
   especially).

## Conventions

- Shell, POSIX-compatible bash; 2-space or 4-space indentation consistent per file.
- Errors to stderr (`err()` helpers exist in update-ai / clear-ai-cache — reuse the
  pattern); progress logs to stderr too, so `code`'s menus stay clean on stdout.
- Small-model users: see the `small-model-context` skill in `.agents/skills/` for
  context-economy rules (MISSING_CONTEXT protocol, PROJECT_MAP pattern). Load it
  when running 7B-class local models; ignore otherwise.

## Testing

No test suite. Verify by running `bash -n <script>` for syntax, and on-device:
`doctor-ai` (checks installs + API reachability), then the flow you changed in a
fresh proot container if it's installer logic.
