# Android AI Development Environment

This project is a set of scripts to install Ollama, proot distro Ubuntu, and Aider in an Android environment with minimal effort. Setup instructions:
- mkdir -p projects
- git clone git@github.com:cjl4hd/OllamaAiderAndroid.git
- git pull
- update-ai
- code

Todo:
- Verify setup / update / run scripts on another phone
- add support for optional plugins/tools:
- whisper
- kiwix
- ssh

## Hardware
- Samsung Galaxy S26 (Snapdragon)
- Android
- Termux
- Ubuntu (proot-distro)

## Architecture
```
Android
└── Termux
    ├── Ollama
    │   └── qwen-coder-7b
    ├── proot-distro
    │   └── Ubuntu
    │       └── Aider
    │       └── projects (git) 
    └── helper scripts
```
## Models

Android Storage:
/storage/emulated/0/Models/

Imported into Ollama using:

FROM /data/data/com.termux/files/home/storage/shared/Models/qwen2.5-coder-7b-instruct-q4_k_m.gguf

This allows you to download models on your phone and point to them from Termux/ubuntu. I created a Models directory in my android home directory to separate from Downloads. These files are imported into Ollama for management, meaning you can delete them from the model directory once imported. 

Create:

ollama create qwen-coder-7b -f Modelfile

## Start Coding

code

This command lets you choose your AI model and project, then runs ollama server and aider client in the project directory. 

## Important Commands

- add_models.sh
- code
- doctor-ai
- update-ai
- Ubuntu.sh
- uv_aider_install.sh

## Notes

Projects are stored in proot ubuntu:

~/projects

Visible as:

/root/projects

inside Ubuntu.

Models remain in:

~/storage/shared/Models
