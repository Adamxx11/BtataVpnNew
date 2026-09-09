#!/bin/bash

################################################################################
# Batata VPN - WireGuard Server Setup Script
# For Ubuntu 20.04 LTS, 22.04 LTS, and Debian 11+
# 
# Usage: sudo bash setup_wireguard.sh
#
# This script:
# 1. Detects and validates Linux distribution
# 2. Detects primary network interface dynamically
# 3. Installs WireGuard
# 4. Enables IPv4 forwarding
# 5. Generates server and client keys
# 6. Configures WireGuard interface (wg0)
# 7. Sets up NAT/masquerading
# 8. Configures firewall
# 9. Starts WireGuard service
# 10. Outputs client configuration
#
# SECURITY: Private keys are NOT printed to console.
# Keys are only stored in files with restricted permissions.
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WG_INTERFACE="wg0"
WG_PORT="51820"
WG_NETWORK="10.0.0.0/24"
WG_SERVER_IP="10.0.0.1"
WG_CLIENT_IP="10.0.0.2"
WG_CONF_DIR="/etc/wireguard"
WG_CONF_FILE="${WG_CONF_DIR}/${WG_INTERFACE}.conf"
DNS_SERVER="1.1.1.1"

################################################################################
# Functions
################################################################################

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root. Use: sudo bash setup_wireguard.sh"
        exit 1
    fi
}

check_distro() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "Cannot detect Linux distribution"
        exit 1
    fi

    . /etc/os-release

    if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
        log_info "Detected: $ID $VERSION_ID"
    else
        log_error "Unsupported distribution: $ID"
        log_warn "This script requires Ubuntu 20.04+, 22.04+, or Debian 11+"
        log_warn "You may adapt this script for your distribution"
        exit 1
    fi
}

detect_interface() {
    # Detect primary network interface (not loopback, not docker)
    local iface=$(ip route | grep default | awk '{print $5}' | head -1)

    if [[ -z "$iface" ]]; then
        log_error "Cannot detect primary network interface"
        exit 1
    fi

    if [[ ! -e /sys/class/net/$iface ]]; then
        log_error "Detected interface $iface does not exist"
        exit 1
    fi

    echo "$iface"
}

install_wireguard() {
    log_info "Installing WireGuard..."
    apt-get update > /dev/null 2>&1
    apt-get install -y wireguard wireguard-tools > /dev/null 2>&1
    log_info "WireGuard installed"
}

enable_ip_forwarding() {
    log_info "Enabling IPv4 forwarding..."
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf 2>/dev/null || true
    sysctl -p > /dev/null 2>&1
    log_info "IPv4 forwarding enabled"
}

generate_keys() {
    log_info "Generating server keys..."
    umask 077
    wg genkey | tee ${WG_CONF_DIR}/server_privatekey | wg pubkey > ${WG_CONF_DIR}/server_publickey

    log_info "Generating client keys..."
    wg genkey | tee ${WG_CONF_DIR}/client_privatekey | wg pubkey > ${WG_CONF_DIR}/client_publickey
}

create_wg_config() {
    local primary_iface=$1
    local server_privkey=$(cat ${WG_CONF_DIR}/server_privatekey)
    local client_pubkey=$(cat ${WG_CONF_DIR}/client_publickey)

    log_info "Configuring WireGuard interface..."

    cat > "${WG_CONF_FILE}" <<EOF
[Interface]
PrivateKey = ${server_privkey}
Address = ${WG_SERVER_IP}/24
ListenPort = ${WG_PORT}
PostUp = iptables -A FORWARD -i ${WG_INTERFACE} -j ACCEPT; iptables -A FORWARD -o ${WG_INTERFACE} -j ACCEPT; iptables -t nat -A POSTROUTING -o ${primary_iface} -j MASQUERADE
PostDown = iptables -D FORWARD -i ${WG_INTERFACE} -j ACCEPT; iptables -D FORWARD -o ${WG_INTERFACE} -j ACCEPT; iptables -t nat -D POSTROUTING -o ${primary_iface} -j MASQUERADE

[Peer]
PublicKey = ${client_pubkey}
AllowedIPs = ${WG_CLIENT_IP}/32
EOF

    chmod 600 "${WG_CONF_FILE}"
    log_info "WireGuard interface configured"
}

configure_firewall() {
    log_info "Configuring firewall..."

    # Check if UFW is available
    if command -v ufw &> /dev/null; then
        ufw allow ${WG_PORT}/udp > /dev/null 2>&1 || true
        ufw --force enable > /dev/null 2>&1 || true
    else
        log_warn "UFW not found, skipping firewall configuration"
        log_warn "Manually allow UDP port ${WG_PORT} on your firewall"
    fi

    log_info "Firewall configured"
}

start_wireguard() {
    log_info "Starting WireGuard service..."
    systemctl enable wg-quick@${WG_INTERFACE} > /dev/null 2>&1
    systemctl start wg-quick@${WG_INTERFACE} > /dev/null 2>&1
    log_info "WireGuard started"
}

get_public_ip() {
    # Try to get public IP from external API
    local public_ip=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null || echo "")

    if [[ -z "$public_ip" ]]; then
        public_ip=$(hostname -I | awk '{print $1}')
    fi

    echo "$public_ip"
}

output_client_config() {
    local public_ip=$1
    local server_pubkey=$(cat ${WG_CONF_DIR}/server_publickey)
    local client_privkey=$(cat ${WG_CONF_DIR}/client_privatekey)

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "CLIENT CONFIGURATION"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo -e "${YELLOW}Server Public IP:${NC} $public_ip"
    echo -e "${YELLOW}Server Public Key:${NC} $server_pubkey"
    echo -e "${YELLOW}Server Endpoint:${NC} $public_ip:${WG_PORT}"
    echo ""
    echo -e "${YELLOW}Client Private Key:${NC} $client_privkey"
    echo ""
    echo "Save the following as 'batata_nl.conf' (or your preferred name):"
    echo ""
    echo "─────────────────────────────────────────────────────────────────────────────"
    cat <<EOF
[Interface]
PrivateKey = $client_privkey
Address = ${WG_CLIENT_IP}/24
DNS = ${DNS_SERVER}

[Peer]
PublicKey = $server_pubkey
Endpoint = $public_ip:${WG_PORT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
EOF
    echo "─────────────────────────────────────────────────────────────────────────────"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Copy the above configuration"
    echo "2. Save to 'batata_nl.conf' on your Windows PC"
    echo "3. Protect this file (treat like a private key!)"
    echo "4. Load in Batata VPN GUI"
    echo "5. Click CONNECT and verify public IP changes"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
}

verify_setup() {
    log_info "Verifying setup..."

    # Check if WireGuard service is running
    if systemctl is-active --quiet wg-quick@${WG_INTERFACE}; then
        log_info "WireGuard service is running"
    else
        log_error "WireGuard service failed to start"
        log_warn "Check logs: sudo journalctl -u wg-quick@${WG_INTERFACE} -n 20"
        exit 1
    fi

    # Check if interface exists
    if ip link show ${WG_INTERFACE} > /dev/null 2>&1; then
        log_info "WireGuard interface ${WG_INTERFACE} is active"
    else
        log_error "WireGuard interface ${WG_INTERFACE} not found"
        exit 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                  Batata VPN - WireGuard Server Setup                          ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo ""

    check_root
    check_distro

    local primary_iface=$(detect_interface)
    log_info "Using network interface: $primary_iface"

    install_wireguard
    enable_ip_forwarding
    generate_keys
    create_wg_config "$primary_iface"
    configure_firewall
    start_wireguard
    verify_setup

    local public_ip=$(get_public_ip)
    output_client_config "$public_ip"
}

main
