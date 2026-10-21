# Working on OllamaAiderAndroid (agent guide)

Read this before making changes. Follows the [AGENTS.md](https://agents.md) convention
so any coding agent picks it up; `CLAUDE.md` just points here.

## What this is

Installer and launcher scripts for an on-device AI coding environment: Termux (host)
runs **llama.cpp (`llama-server`, the primary engine — Ollama was retired in the
Phase-3 engine migration and its model blobs remain usable)**, a proot-distro
Ubuntu container runs Aider, OpenCode and BMoE (`bmoe-cli`, the flash-streamed MoE
engine), and helper scripts tie it all together. The audience is a phone with
limited RAM and storage — assume nothing about the host beyond Termux + Android
storage access.

## Project map

- `update-ai` — the installer/updater. Runs in Termux host only. Creates
  `~/.ai-env.conf`, installs/updates Ubuntu proot, Python/uv/Aider (in Ubuntu),
  llama.cpp (`pkg llama-cpp`), OpenCode (in Ubuntu, optional), the BigMoeOnEdge
  engine (pull + build + `bmoe-arm64/install.sh` inside the `BMOE_PROJECT_DIR`
  clone — best-effort, warnings-not-deaths), storage symlinks, bin links;
  optionally uninstalls the retired Ollama package (model blobs stay).
- `code` — interactive Termux (host) launcher, host-only responsibilities:
  the llama.cpp server and its tuning (`-t 4` measured best on the S26,
  `--alias llama-<filename>` replaces sha256-blob ids in `/v1/models`,
  `LLAMA_MODEL=auto` loads the newest .gguf — with a pick list when several
  models exist; Enter/EOF keeps the auto pick so scripted starts stay
  deterministic; `LLAMA_CONTEXT_LENGTH`/`LLAMA_MODELS_DIR` config keys),
  GGUF import (idempotent: picking a file already in the shared models dir
  is "already imported", not an error — `GGUF_DIR` and `LLAMA_MODELS_DIR`
  both default to `android-home/models`), benchmarks (menu 7), cache menu,
  and menu option 9 = one proot session running `code-ubuntu` (menu
  renumbered when Ollama menus retired — check the actual menu before
  referencing numbers). It no longer launches container apps through wrapped
  `bash -lc` strings — that wrapper class produced the repo's worst bugs
  (PATH-export TUI wedge, brace-group parse error) and is gone.
- `code-ubuntu` — the Ubuntu-side launcher: model/project pickers (via the
  llama.cpp HTTP API — works from the container, no host CLI needed), aider /
  opencode / freebuff launches by absolute path with no PATH exports,
  **bmoe stream-chat launcher** (`bmoe` subcommand + menu 6: model picker
  over the shared models dir, tunables `BMOE_CACHE_MB`/`BMOE_THREADS`/
  `BMOE_IO_THREADS`, `BMOE_BIN` override; works with llama-server down),
  OpenCode config generation (writes the Ubuntu home natively), adb-ai
  delegation, pre-launch quick-clean hook. Runs both via `code` option 9 AND
  bare in an `ubuntu` shell (linked into /usr/local/bin by update-ai).
  Subcommands: aider|opencode|freebuff|regen-oc|mem|bmoe|status. The generated
  OpenCode config must include `limit.output` for every model: OpenCode's
  schema requires it, and a schema-invalid config kills the TUI silently at
  startup (no error, no render).
- `doctor-ai` — health checks and version report. Detects running INSIDE
  proot (nested: Freebuff/nested sessions see this) and then probes the
  local rootfs directly instead of nesting — and base server-running on
  the health endpoint there: `pgrep` can never see the host's llama-server
  process from inside the container.
- `clear-ai-cache` — tiered cache cleanup (Tier 1 safe / Tier 2 destructive, each
  prompted). Detects nested proot via parent-process walk.
- `adb-ai` and `code-ubuntu` — run inside proot Ubuntu only: adb-ai pairs/connects wireless adb to the
  phone itself over loopback, then reduces **Android** memory in tiers (0 info,
  1 kill list incl. Facebook/Instagram + cached-process kills, 2 persistent
  device_config/settings with saved originals + `revert` — phantom process
  killer off lives here, 3 root-gated). Freezes are tracked in
  `~/.config/adb-ai/frozen.txt` (only packages we disabled) so
  `apps --unfreeze-all` inverts exactly our actions. Config
  `~/.adb-ai.conf` in the Ubuntu home; state/backups in `~/.config/adb-ai/`.
- `ubuntu` — plain shell into the Ubuntu container (`proot-distro login`).
- `aider-ubuntu` — runs aider inside Ubuntu with argument passthrough via the
  `bash -lc 'aider "$@"' bash "$@"` trick. `aider-ubuntu.txt` is a tutorial
  explaining that trick — keep it in sync if the wrapper changes.
- `add_models.sh` — legacy `ollama create` one-shot; superseded by `code` menu 2
  (file import) and kept for the old Modelfiles only.
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
   Python version, project dir, GGUF dir, llama.cpp server port/model/ctx,
   BMOE tunables — source it, apply defaults with `:-`, never hardcode paths.
   New tunables go in the config file and the `update-ai` usage text together.
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
9. **Non-interactive proot shells hide PATH and punish PATH injection.**
   `bash -lc` never sources rc-file PATH additions (nvm installs append to
   `.bashrc` behind Ubuntu's interactive-only guard), so resolve binaries via
   explicit candidate paths (`ubuntu_which` in `code`, `in_ubuntu_path` in
   `doctor-ai`) — never `command -v`. Launch TUI apps by absolute path **without**
   extending PATH in the launch string: an `export PATH=...` prefix wedged
   opencode's startup on device (bisect-verified: cd + absolute-path binary
   renders; PATH-export + binary hangs). npm shims are `#!/usr/bin/env node`:
   in a non-interactive shell `env` cannot resolve node either — run the shim
   via node's absolute path instead (freebuff needed this; `ubuntu_which node`).
   `update-ai`'s `run_in_ubuntu` may still export PATH — its commands are
   non-interactive one-shots, where the prefix is proven harmless.

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

`bash -n` is necessary but not sufficient — it cannot catch logic corruption (a
merged-line edit once passed syntax while silently breaking a generator loop) or
schema rejection (a generated config was syntactically fine bash but failed the
consumer tool's validation). For functions that write files or assemble command
strings: execute the real function with stubbed dependencies and validate its
actual output. For on-device hangs, bisect the ingredients (cd / PATH / binary,
one variable at a time) instead of reasoning from the full composite — session
experience: the composite "obvious" suspect was wrong twice.

adb-ai specifics (device-verified on SM-S942U1): an `adb` client inside proot
must never hold the caller's stdout pipe — daemon-spawning calls and blocked
mdns wedge the shell indefinitely; redirect to files, use `timeout -k`, and
`</dev/null` (see `adbx`/`mdns_ports`/`device_listed` in adb-ai). Samsung's
`dumpsys meminfo` section is `380,893K: pkg` (uppercase K, no space) vs AOSP's
`380,893 kB: pkg` — parse both. `/proc/swaps` is SELinux-blocked from adb shell;
use meminfo's SwapTotal/SwapFree. mdns discovery is dead from inside proot, but
proot shares the phone's network namespace — auto-reconnect scans loopback with
pure-bash `/dev/tcp` probes (fork-free concurrency counter; a `jobs|wc` throttle
forks 2 processes per probe and triples the runtime) and verifies each open port
with a real `adb connect`. Variadic flag parsing: collect package args only up
to the next `--flag`, then reprocess that flag — the outer shift discards it
otherwise.
