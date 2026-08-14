#!/usr/bin/env python3

import argparse
import csv
import os
import re
import subprocess
import time
from pathlib import Path

PROMPTS = [
    ("coding", "Write a Python function that implements quicksort."),
    ("coding", "Implement breadth-first search in Python."),
    ("coding", "Write a Bash script that recursively finds all jpg files."),
    ("reasoning", "If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?"),
    ("reasoning", "Find the next number in the sequence: 2, 6, 18, 54."),
    ("knowledge", "Explain TCP versus UDP."),
    ("knowledge", "Explain how a heat pump works."),
    ("instruction", "List exactly seven fruits."),
    ("instruction", "Respond only in valid JSON describing a bicycle."),
    ("workflow", "Write a Termux shell script that renames all PNG files."),
]

PROMPT_TPS_RE = re.compile(r"prompt eval time.*?([\d.]+)\s*tokens/sec")
DECODE_TPS_RE = re.compile(r"eval time.*?([\d.]+)\s*tokens/sec")


def get_memory(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except:
        pass

    return 0


def run_prompt(model, llama_cli, prompt, n_predict):

    cmd = [
        llama_cli,
        "-m",
        model,
        "-n",
        str(n_predict),
        "-p",
        prompt,
        "--no-display-prompt",
    ]

    start = time.time()

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    peak_mem = 0

    while process.poll() is None:
        peak_mem = max(peak_mem, get_memory(process.pid))
        time.sleep(0.1)

    stdout, stderr = process.communicate()

    elapsed = time.time() - start

    prompt_tps = None
    decode_tps = None

    p = PROMPT_TPS_RE.search(stderr)
    if p:
        prompt_tps = float(p.group(1))

    d = DECODE_TPS_RE.search(stderr)
    if d:
        decode_tps = float(d.group(1))

    return {
        "elapsed_s": round(elapsed, 2),
        "prompt_tps": prompt_tps,
        "decode_tps": decode_tps,
        "peak_memory_mb": round(peak_mem, 1),
        "response": stdout.strip(),
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--model", required=True)
    parser.add_argument("--llama-cli", default="llama-cli")
    parser.add_argument("--tokens", type=int, default=128)
    parser.add_argument("--output", default="benchmark.csv")

    args = parser.parse_args()

    rows = []

    for i, (category, prompt) in enumerate(PROMPTS, start=1):

        print(f"[{i}/{len(PROMPTS)}] {category}")

        result = run_prompt(
            args.model,
            args.llama_cli,
            prompt,
            args.tokens,
        )

        rows.append(
            {
                "category": category,
                "prompt": prompt,
                **result,
            }
        )

    with open(args.output, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
