# Android AI Development Environment

## Hardware
- Samsung Galaxy S26 (Snapdragon)
- Android
- Termux
- Ubuntu (proot-distro)

## Architecture

Android
└── Termux
    ├── Ollama
    │   └── qwen-coder-7b
    ├── proot-distro
    │   └── Ubuntu
    │       └── Aider
    └── helper scripts

## Models

Android Storage:
/storage/emulated/0/Models/

Imported into Ollama using:

FROM /data/data/com.termux/files/home/storage/shared/Models/qwen2.5-coder-7b-instruct-q4_k_m.gguf

Create:

ollama create qwen-coder-7b -f Modelfile

## Start Coding

code

Equivalent:

proot-distro login ubuntu -- bash -lc \
'aider --model ollama_chat/qwen-coder-7b'

## Important Commands

Start Ollama

ollama serve

List models

ollama list

Update Aider

pipx upgrade aider-chat

Update Termux

pkg update
pkg upgrade

Update Ubuntu

proot-distro login ubuntu

apt update
apt upgrade

## Notes

Projects are stored in:

~/projects

Visible as:

/root/projects

inside Ubuntu.

Models remain in:

~/storage/shared/Models
