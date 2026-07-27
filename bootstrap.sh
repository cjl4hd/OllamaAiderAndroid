#Assuming we're in the OllamaAiderAndroid project dir
#First pull git repo to ensure we have latest
git pull

#check if proot environment exists and works
#if env is no good or doesn't exist, build proot environment

#check if python env is setup / up to date
#if not, setup python virtual environment and install ollama and aider

source uv_aider_install.sh

#we will keep all scripts in the git repo and soft link to them to make management easier
UBUNTU_HOME="data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/ubuntu"
TERMUX_HOME="/data/data/com.termux/files/home"
ANDROID_HOME="/storage/emulated/0/"

#copy soft links into both termux dir, --no-dereference copies soft link instead of contents

#copy soft links into  ubuntu home dirr

#copy soft links into bin path

