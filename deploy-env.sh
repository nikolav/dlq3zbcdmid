#!/bin/bash

# update packages
apt update
apt-get update -y

# install git
apt install git
git config --global user.name "nikolav"
git config --global user.email "admin@nikolav.rs"

# install docker
apt-get remove docker docker-engine docker.io containerd runc
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# install docker-compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose


## install selenium chrome webdriver
## https://github.com/password123456/setup-selenium-with-chrome-driver-on-ubuntu_debian
## https://chatgpt.com/c/24e8ac36-02ac-4688-8ae4-a7062929978e


# allow app @ports
ufw allow OpenSSH
ufw allow http
ufw allow https
ufw allow 5544
ufw enable

# shortcuts
alias ll='ls -AlFht --color=auto --group-directories-first '
alias gs='git status '

# status check
echo '== status'
git --version
docker --version
docker-compose --version
service docker status
ufw status verbose
