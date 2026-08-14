#!/usr/bin/env python3

import csv
import re
import subprocess
import time
from pathlib import Path

MODELS_DIR = Path.home() / "storage/shared/Models"

OUTPUT_CSV = "benchmark_results.csv"
LEADERBOARD = "leaderboard.md"

PROMPTS = [
    ("workflow", "Write a Termux shell script that renames PNG files."),
    ("workflow", "Debug an Ollama installation."),
    ("coding", "Implement breadth-first search in Python."),
    ("reasoning", "What comes next: 2, 6, 18, 54?"),
    ("knowledge", "Explain TCP vs UDP."),
]

PROMPT_TPS = re.compile(r"prompt eval time.*?([\d.]+)\s+tokens per second")

DECODE_TPS = re.compile(r"eval time.*?([\d.]+)\s+tokens per second")

LOAD_TIME = re.compile(r"load time\s+=\s+([\d.]+)\s+ms")


def parse_model_name(path):

    name = path.stem

    quant = "unknown"

    q = re.search(r"(Q\d[_A-Z0-9]*)", name)

    if q:
        quant = q.group(1)

    params = "unknown"

    p = re.search(r"(\d+(?:\.\d+)?)B", name, re.I)

    if p:
        params = p.group(1) + "B"

    return params, quant


def benchmark_hardware(model):

    cmd = [
        "llama-bench",
        "-m",
        str(model),
        "-o",
        "csv",
        "-r",
        "3",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    return result.stdout


def benchmark_prompt(model, prompt):

    cmd = [
        "llama-cli",
        "--perf",
        "-m",
        str(model),
        "-n",
        "128",
        "--no-display-prompt",
        "-p",
        prompt,
    ]

    start = time.time()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    runtime = time.time() - start

    stderr = result.stderr

    prompt_tps = ""
    decode_tps = ""
    load_time = ""

    m = PROMPT_TPS.search(stderr)

    if m:
        prompt_tps = m.group(1)

    m = DECODE_TPS.search(stderr)

    if m:
        decode_tps = m.group(1)

    m = LOAD_TIME.search(stderr)

    if m:
        load_time = m.group(1)

    return {
        "runtime": round(runtime, 2),
        "load_ms": load_time,
        "prompt_tps": prompt_tps,
        "decode_tps": decode_tps,
    }


rows = []

models = sorted(MODELS_DIR.glob("*.gguf"))

for model in models:

    print()
    print("=" * 70)
    print(model.name)
    print("=" * 70)

    params, quant = parse_model_name(model)

    print("Hardware benchmark...")

    benchmark_hardware(model)

    prompt_scores = []

    decode_scores = []

    for category, prompt in PROMPTS:

        print(" ", category)

        result = benchmark_prompt(model, prompt)

        if result["prompt_tps"]:
            prompt_scores.append(float(result["prompt_tps"]))

        if result["decode_tps"]:
            decode_scores.append(float(result["decode_tps"]))

    avg_prompt = (
        sum(prompt_scores) / len(prompt_scores)
        if prompt_scores
        else 0
    )

    avg_decode = (
        sum(decode_scores) / len(decode_scores)
        if decode_scores
        else 0
    )

    rows.append(
        {
            "model": model.name,
            "parameters": params,
            "quantization": quant,
            "prompt_tps": round(avg_prompt, 2),
            "decode_tps": round(avg_decode, 2),
        }
    )

with open(OUTPUT_CSV, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=rows[0].keys(),
    )

    writer.writeheader()

    writer.writerows(rows)

rows.sort(
    key=lambda x: x["decode_tps"],
    reverse=True,
)

with open(LEADERBOARD, "w") as f:

    f.write("| Rank | Model | Quant | Prompt | Decode |\n")
    f.write("|---|---|---|---:|---:|\n")

    for i, row in enumerate(rows, 1):

        f.write(
            f"| {i} | "
            f"{row['model']} | "
            f"{row['quantization']} | "
            f"{row['prompt_tps']} | "
            f"{row['decode_tps']} |\n"
        )

print()
print("Results written:")
print(OUTPUT_CSV)
print(LEADERBOARD)
