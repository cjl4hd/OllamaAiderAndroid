#!/data/data/com.termux/files/usr/bin/bash
# Import the Modelfiles in this repo as Ollama models.
# GGUFs are expected in the shared models dir (GGUF_DIR from ~/.ai-env.conf,
# default /storage/emulated/0/Models), matching what 'code' > Import GGUF uses.
set -e

CONFIG_FILE="$HOME/.ai-env.conf"
[ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE"
GGUF_DIR="${GGUF_DIR:-$HOME/storage/shared/Models}"

MODELS=(
    "Qwen3.5-4B-Q4_K_M"
    "gemma-4-E2B-it-Q4_K_M"
    "qwen2.5-coder-7b-instruct-q4_k_m"
)

for MODEL in "${MODELS[@]}"; do
    GGUF="$GGUF_DIR/$MODEL.gguf"
    if [ ! -f "$GGUF" ]; then
        echo "SKIP: $GGUF not found"
        continue
    fi
    TMP=$(mktemp)
    echo "FROM \"$GGUF\"" > "$TMP"
    ollama create "$MODEL" -f "$TMP"
    rm -f "$TMP"
    echo "OK: $MODEL"
done
