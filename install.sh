#!/usr/bin/env bash

set -e
set -o pipefail

########################################
# TeleTube Installer
# Author: AmirH-TI
########################################

PROJECT_NAME="TeleTube"
REPO_URL="https://github.com/amirh-ti/TeleTube.git"
INSTALL_DIR="/opt/TeleTube"
SERVICE_NAME="TeleTube"

########################################
# Colors
########################################

RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
CYAN="\033[1;36m"
RESET="\033[0m"

########################################
# Messages
########################################

info() {
    echo -e "${BLUE}[INFO]${RESET} $1"
}

success() {
    echo -e "${GREEN}[ OK ]${RESET} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${RESET} $1"
}

error() {
    echo -e "${RED}[FAIL]${RESET} $1"
}

########################################
# Banner
########################################

clear

echo -e "${CYAN}"
cat << "EOF"

████████╗███████╗██╗     ███████╗████████╗██╗   ██╗██████╗ ███████╗
╚══██╔══╝██╔════╝██║     ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝
   ██║   █████╗  ██║     █████╗     ██║   ██║   ██║██████╔╝█████╗
   ██║   ██╔══╝  ██║     ██╔══╝     ██║   ██║   ██║██╔══██╗██╔══╝
   ██║   ███████╗███████╗███████╗   ██║   ╚██████╔╝██████╔╝███████╗
   ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝

EOF

echo -e "${RESET}"

echo
info "Starting TeleTube installation..."
echo

########################################
# Root Check
########################################

if [[ $EUID -ne 0 ]]; then
    error "Please run this installer as root."
    exit 1
fi

success "Running as root."

########################################
# Detect OS
########################################

if [[ ! -f /etc/os-release ]]; then
    error "Unsupported operating system."
    exit 1
fi

source /etc/os-release

case "$ID" in
    ubuntu|debian)
        success "Detected $PRETTY_NAME"
        ;;
    *)
        error "Only Ubuntu and Debian are supported."
        exit 1
        ;;
esac

########################################
# Update packages
########################################

info "Updating package lists..."

apt-get update -y

success "Package lists updated."

########################################
# Install packages
########################################

PACKAGES=(
    git
    curl
    wget
    python3
    python3-pip
    python3-venv
    ffmpeg
    aria2
)

info "Installing required packages..."

for pkg in "${PACKAGES[@]}"
do
    if dpkg -s "$pkg" >/dev/null 2>&1; then
        success "$pkg already installed."
    else
        info "Installing $pkg ..."
        apt-get install -y "$pkg"
    fi
done

success "All packages installed."

########################################
# Install Deno
########################################

if command -v deno >/dev/null 2>&1
then
    success "Deno already installed."
else
    info "Installing Deno..."

    curl -fsSL https://deno.land/install.sh | sh

    export DENO_INSTALL="/root/.deno"
    export PATH="$DENO_INSTALL/bin:$PATH"

    if command -v deno >/dev/null 2>&1
    then
        success "Deno installed."
    else
        error "Failed to install Deno."
        exit 1
    fi
fi

########################################
# Continue...
########################################

echo
success "System dependencies are ready."
echo
########################################
# Clone / Update Project
########################################

if [[ -d "$INSTALL_DIR/.git" ]]
then
    warn "Existing installation detected."

    info "Updating project..."

    cd "$INSTALL_DIR"

    git fetch --all
    git reset --hard origin/main

    success "Project updated."

else

    info "Cloning project..."

    git clone "$REPO_URL" "$INSTALL_DIR"

    success "Project downloaded."

fi

########################################
# Enter Project Directory
########################################

cd "$INSTALL_DIR"

########################################
# Python Virtual Environment
########################################

if [[ -d venv ]]
then
    success "Virtual environment already exists."
else
    info "Creating virtual environment..."

    python3 -m venv TeleTube

    success "Virtual environment created."
fi

########################################
# Activate Virtual Environment
########################################

source TeleTube/bin/activate

########################################
# Upgrade pip
########################################

info "Upgrading pip..."

pip install --upgrade pip wheel setuptools

########################################
# Install Python Packages
########################################

info "Installing Python requirements..."

pip install -r requirements.txt

success "Python packages installed."

########################################
# Environment File
########################################

if [[ ! -f .env ]]
then

    if [[ -f .env.example ]]
    then
        cp .env.example .env
        success ".env created."
    else
        touch .env
        success ".env created."
    fi

else

    warn ".env already exists."

fi

########################################
# Configuration Wizard
########################################

echo
echo "--------------------------------------"
echo " TeleTube Configuration"
echo "--------------------------------------"
echo

read -rp "Telegram Bot Token: " TELEGRAM_TOKEN
read -rp "Telegram API ID: " API_ID
read -rp "Telegram API HASH: " API_HASH
read -rp "Telethon Session String: " SESSION_STRING
read -rp "Target Channel URL: " TARGET_CHANNEL
read -rp "Target Channel Username: " TARGET_CHANNEL_USERNAME
read -rp "AUTO_SELECT_TIMEOUT (default 15s):  " AUTO_SELECT_TIMEOUT

cat > .env <<EOF
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
API_ID=$API_ID
API_HASH=$API_HASH
SESSION_STRING=$SESSION_STRING

TARGET_CHANNEL=$TARGET_CHANNEL
TARGET_CHANNEL_USERNAME=$TARGET_CHANNEL_USERNAME
AUTO_SELECT_TIMEOUT=$AUTO_SELECT_TIMEOUT

DOWNLOAD_DIR=/root/TeleTube/youtube_memory
COOKIES_FILE=/root/TeleTube/cookies.txt
EOF

success ".env configured."

########################################
# Verify Configuration
########################################

echo
info "Installed path : $INSTALL_DIR"
info "Python         : $(python3 --version)"
info "Pip            : $(pip --version | awk '{print $2}')"

echo
success "Project installation completed."
echo
########################################
# Create systemd service
########################################

info "Creating systemd service..."

cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=TeleTube Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple

WorkingDirectory=${INSTALL_DIR}

ExecStart=${INSTALL_DIR}/TeleTube/bin/python3 bot.py

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=10

User=root
Group=root

Environment=PYTHONUNBUFFERED=1
Environment="PATH=/root/.deno/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

success "Service created."

########################################
# Enable Service
########################################

info "Reloading systemd..."

systemctl daemon-reload

info "Enabling service..."

systemctl enable ${SERVICE_NAME}

########################################
# Start Service
########################################

info "Starting service..."

systemctl restart ${SERVICE_NAME}

sleep 3

########################################
# Check Status
########################################

if systemctl is-active --quiet ${SERVICE_NAME}
then
    success "TeleTube started successfully."
else
    error "TeleTube failed to start."

    echo
    journalctl -u ${SERVICE_NAME} -n 50 --no-pager
    exit 1
fi

########################################
# Finished
########################################

clear

echo
echo "==============================================="
echo "          TeleTube Installed Successfully"
echo "==============================================="
echo
echo "Installation Directory:"
echo "  ${INSTALL_DIR}"
echo
echo "Service Name:"
echo "  ${SERVICE_NAME}"
echo
echo "Useful Commands"
echo
echo "Start Service:"
echo "  systemctl start ${SERVICE_NAME}"
echo
echo "Stop Service:"
echo "  systemctl stop ${SERVICE_NAME}"
echo
echo "Restart Service:"
echo "  systemctl restart ${SERVICE_NAME}"
echo
echo "Service Status:"
echo "  systemctl status ${SERVICE_NAME}"
echo
echo "Live Logs:"
echo "  journalctl -u ${SERVICE_NAME} -f"
echo
echo "Configuration:"
echo "  nano ${INSTALL_DIR}/.env"
echo
echo "Project Directory:"
echo "  cd ${INSTALL_DIR}"
echo
echo "==============================================="
echo
success "Installation completed."
echo
