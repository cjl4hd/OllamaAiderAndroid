curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.12
uv tool install aider-chat --python 3.12
aider --version
