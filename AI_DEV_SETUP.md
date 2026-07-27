# Android AI Development Environment

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

code
doctor-ai
update-ai

## Notes

Projects are stored in:

~/projects

Visible as:

/root/projects

inside Ubuntu.

Models remain in:

~/storage/shared/Models
