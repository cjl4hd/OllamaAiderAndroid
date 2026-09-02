---
name: small-model-context
description: Context-economy and discipline rules for coding agents on small local models (7B-class, e.g. qwen-coder via Ollama/Aider on-device). Load when the target model is small; ignore for capable cloud models.
---

# Small-model agent discipline

For 7B-class models the binding constraint is context and instruction-following,
not knowledge. Every rule below exists to stop a small model from burning context
or hallucinating. When running capable models, do not apply this skill.

## Prompt guard (`.aider.conventions.md` pattern)

- **Explicit output only.** No pleasantries, no narration of intent, no "I will
  now..." — output the answer or the diff immediately.
- **No hedging.** Pick the change and make it; a confident wrong guess gets caught
  by review, a vague answer helps nobody.
- **Response budget:** explanations capped at ~2 sentences. Code first, prose last.
- **Hallucination protocol:** if a file, function, or path is not in the provided
  workspace context, reply exactly `MISSING_CONTEXT: [Entity]` and stop. Never
  guess names. A stop is cheap; a guessed symbol wastes a whole session.

## Context economy

- **Interface maps over file dumps.** Maintain a `PROJECT_MAP.md`-style file:
  one entry per module with signatures, params, and one-line purpose. Load the
  map + the ONE file being edited, not the repo. Read real files only for
  implementation detail.
- **Small windows.** Read files with offset/limit around the target, never whole
  large files. Search first, then read a few hundred lines.
- **One concern per prompt.** Batch related small edits into one request; never
  ask a small model for multi-step refactors in a single turn.
- **Constraints repeat verbatim.** Small models drop rules mid-session. Repeat
  hard constraints (file format, forbidden actions) inside each prompt, not once
  at the start.

## Repo setup for small models

- Keep a conventions file the tool auto-loads (`.aider.conventions.md` for aider)
  with the guard rules above — the model re-reads it every session.
- Keep `PROJECT_MAP.md` updated when signatures change; a stale map is worse than
  none, because the model trusts it absolutely.
- Prefer `unified diff` output formats where the tool supports them; they are the
  most token-efficient and least hallucination-prone edit format for small models.
- Set low temperature (aider/Ollama default ~0.5 works; deterministic is better
  than creative when editing code).
