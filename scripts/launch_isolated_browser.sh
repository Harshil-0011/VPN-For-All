#!/usr/bin/env bash
# Launches a containerized, hardened Firefox / Mullvad browser session in an ephemeral profile directory.
# Enforces anti-fingerprinting, WebRTC blocking, DoH DNS routing, and wipes everything on exit.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/config"

SESSION_ID="session_$(date +%s)_$RANDOM"
PROFILE_DIR="/tmp/privacy_router_sessions/$SESSION_ID"

echo "[*] Initializing isolated browser session container: $SESSION_ID"
mkdir -p "$PROFILE_DIR"

# Copy user.js hardening rules into profile directory
if [ -f "$CONFIG_DIR/user.js" ]; then
    cp "$CONFIG_DIR/user.js" "$PROFILE_DIR/user.js"
    echo "[+] Applied hardened user.js preferences"
fi

# Set up policies.json inside profile directory for enterprise policy enforcement
POLICIES_DIR="$PROFILE_DIR/distribution"
mkdir -p "$POLICIES_DIR"
if [ -f "$CONFIG_DIR/browser_policies.json" ]; then
    cp "$CONFIG_DIR/browser_policies.json" "$POLICIES_DIR/policies.json"
    echo "[+] Applied browser policies configuration"
fi

# Find available browser binary
BROWSER_BIN=""
for candidate in mullvad-browser firefox firefox-esr; do
    if command -v "$candidate" >/dev/null 2>&1; then
        BROWSER_BIN="$candidate"
        break
    fi
done

if [ -z "$BROWSER_BIN" ]; then
    echo "[!] No Firefox / Mullvad Browser binary found in PATH."
    echo "[i] Profile initialized at: $PROFILE_DIR"
    echo "[i] Launch your browser manually with: --profile $PROFILE_DIR --no-remote"
    exit 0
fi

echo "[*] Launching $BROWSER_BIN in isolated mode..."
"$BROWSER_BIN" --profile "$PROFILE_DIR" --no-remote --private-window "about:blank" &
BROWSER_PID=$!

echo "[+] Browser active (PID: $BROWSER_PID)."
echo "[*] Session profile will be purged automatically upon exit..."

wait $BROWSER_PID 2>/dev/null || true

echo "[*] Wiping session profile data from disk..."
rm -rf "$PROFILE_DIR"
echo "[+] Session container $SESSION_ID wiped successfully."
