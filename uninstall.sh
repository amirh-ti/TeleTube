#!/usr/bin/env bash

set -e
set -o pipefail

########################################
# TeleTube Uninstaller
########################################

PROJECT_NAME="TeleTube"
INSTALL_DIR="/opt/teletube"
SERVICE_NAME="teletube"
DOWNLOAD_DIR="/root/youtube_memory"

RED="\033[1;31m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
CYAN="\033[1;36m"
RESET="\033[0m"

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
warn "This will completely uninstall ${PROJECT_NAME}."
echo

read -rp "Continue? (y/N): " answer

case "$answer" in
    y|Y|yes|YES)
        ;;
    *)
        info "Cancelled."
        exit 0
        ;;
esac

########################################
# Stop Service
########################################

if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then

    info "Stopping service..."

    systemctl stop ${SERVICE_NAME} || true

    info "Disabling service..."

    systemctl disable ${SERVICE_NAME} || true

    rm -f /etc/systemd/system/${SERVICE_NAME}.service

    systemctl daemon-reload

    systemctl reset-failed

    success "Service removed."

else
    warn "Service not found."
fi

########################################
# Remove Project
########################################

if [[ -d "$INSTALL_DIR" ]]; then

    info "Removing project..."

    rm -rf "$INSTALL_DIR"

    success "Project removed."

else
    warn "Project directory not found."
fi

########################################
# Remove Download Directory
########################################

if [[ -d "$DOWNLOAD_DIR" ]]; then

    read -rp "Delete downloaded videos too? (y/N): " del

    if [[ "$del" =~ ^(y|Y|yes|YES)$ ]]; then
        rm -rf "$DOWNLOAD_DIR"
        success "Download directory removed."
    else
        warn "Download directory kept."
    fi

fi

########################################
# Finish
########################################

echo
echo "====================================="
echo " TeleTube Uninstalled Successfully"
echo "====================================="
echo

success "Finished."
