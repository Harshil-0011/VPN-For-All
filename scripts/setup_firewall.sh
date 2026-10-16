#!/usr/bin/env bash
# Automated Linux Firewall Killswitch, Secure DoH Initialization, and Cleanup Script
# Requires root / sudo privileges for iptables/nftables manipulation.

set -e

ACTION="${1:-setup}"
ALLOWED_IFACE="${2:-wg0}"
VPN_SERVER_IP="${3:-}"

echo "======================================================================"
echo " [Crafting-Apps] Local Privacy Routing & Firewall Setup (Linux)"
echo "======================================================================"

enable_killswitch() {
    echo "[*] Enabling iptables zero-leak killswitch..."

    # Flush existing rules
    sudo iptables -F
    sudo iptables -X

    # Set default policies to DROP
    sudo iptables -P INPUT DROP
    sudo iptables -P FORWARD DROP
    sudo iptables -P OUTPUT DROP

    # Allow local loopback traffic
    sudo iptables -A INPUT -i lo -j ACCEPT
    sudo iptables -A OUTPUT -o lo -j ACCEPT

    # Allow established and related connections
    sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

    # Allow outbound traffic on the VPN interface
    sudo iptables -A OUTPUT -o "$ALLOWED_IFACE" -j ACCEPT

    # If VPN Server IP provided, allow outbound UDP/TCP connection to it
    if [ -n "$VPN_SERVER_IP" ]; then
        sudo iptables -A OUTPUT -d "$VPN_SERVER_IP" -j ACCEPT
        echo "[+] Outbound connection allowed to VPN Endpoint: $VPN_SERVER_IP"
    fi

    echo "[+] Linux firewall killswitch active on interface: $ALLOWED_IFACE"
}

disable_killswitch() {
    echo "[*] Disabling firewall killswitch and restoring default traffic policies..."
    sudo iptables -P INPUT ACCEPT
    sudo iptables -P FORWARD ACCEPT
    sudo iptables -P OUTPUT ACCEPT
    sudo iptables -F
    sudo iptables -X
    echo "[+] Firewall killswitch disabled."
}

cleanup_sessions() {
    echo "[*] Purging all ephemeral session directories..."
    TEMP_SESSIONS="/tmp/privacy_router_sessions"
    if [ -d "$TEMP_SESSIONS" ]; then
        rm -rf "${TEMP_SESSIONS:?}"/*
        echo "[+] Temporary session profiles cleared in $TEMP_SESSIONS"
    else
        echo "[+] No ephemeral session directory found."
    fi
}

case "$ACTION" in
    setup|enable)
        enable_killswitch
        ;;
    disable)
        disable_killswitch
        ;;
    clean)
        cleanup_sessions
        ;;
    *)
        echo "Usage: $0 {setup|enable|disable|clean} [vpn_interface] [vpn_server_ip]"
        exit 1
        ;;
esac
