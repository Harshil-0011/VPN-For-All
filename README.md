# # Crafting-Apps Local Privacy Routing & Session Isolation Application

A complete, local-first professional privacy routing, session-isolation, and VPN-management application for Windows and Linux designed to run entirely on your local PC.

Architected after the **Crafting Apps** philosophy: native execution, high performance, local-first file handling, built-in Model Context Protocol (MCP) control channels, zero external paid servers, zero logging, and complete user control.

---

## 📁 Project Directory Structure

```text
.
├── core/                         # Native backend engine handling local interfaces & routing
│   ├── __init__.py
│   ├── network.py                # Network interface enumeration & routing table inspection
│   ├── tunnel.py                 # WireGuard / TUN local tunnel manager
│   ├── firewall.py               # Platform-agnostic firewall/killswitch control (netsh / iptables)
│   ├── session.py                # Ephemeral profile containerization & zero-log disk wipe daemon
│   └── cli.py                    # Lightweight, native CLI control interface
├── config/                       # Privacy routing configuration templates
│   ├── doh_cloudflared.yml       # Cloudflare DoH proxy configuration
│   ├── doh_quad9.yml             # Quad9 DoH proxy configuration
│   ├── browser_policies.json     # Firefox enterprise privacy policies (Disable WebGL/Telemetry)
│   ├── user.js                   # Hardened Firefox anti-fingerprinting & WebRTC preferences
│   ├── routing_defaults.json     # System default privacy routing policy
│   └── network_profiles.json     # Local network privacy profiles
├── scripts/                      # Automated setup and cleanup scripts
│   ├── setup_firewall.sh         # Linux firewall setup (iptables killswitch & session cleanup)
│   ├── setup_firewall.ps1        # Windows PowerShell firewall killswitch setup
│   ├── launch_isolated_browser.sh# Launches ephemeral hardened browser session on Linux
│   └── launch_isolated_browser.ps1 # Launches ephemeral hardened browser session on Windows
├── mcp/                          # Agent-Ready Control Channel
│   ├── server.py                 # Standard MCP (Model Context Protocol) JSON-RPC stdio server
│   └── client_test.py            # Local agent harness testing MCP channel tools
├── docs/                         # Architecture & Zero-Log verification guide
│   └── ARCHITECTURE.md           # Visual architecture diagrams and design details
├── tests/                        # Unit test suite
│   ├── test_core.py              # Tests for /core modules
│   └── test_mcp.py               # Tests for /mcp server tools
├── verify_privacy.py             # Diagnostic script verifying DNS leaks, WebRTC protection & zero-logs
└── README.md                     # Application documentation
```

---

## ⚡ Key Components & Features

### 1. Native Backend Engine (`/core`)
- **`core/network.py`**: Enumerates network interfaces and reads platform routing tables for Windows (`route print`) and Linux (`ip route`).
- **`core/tunnel.py`**: Manages WireGuard tunnel states locally (`wg-quick` / `wg` CLI) without cloud dependencies.
- **`core/firewall.py`**: Enforces a strict zero-leak killswitch using `iptables` on Linux and `netsh advfirewall` on Windows. Blocks non-VPN outbound leaks if the tunnel drops.
- **`core/session.py`**: Creates temporary, containerized browser profiles on disk, applies zero-log metadata, and securely zeros and purges profile data on exit.
- **`core/cli.py`**: Web-view free, lightweight command-line interface to inspect active tunnels, network interfaces, firewall status, and zero-log policy state.

### 2. Local DNS Security & Browser Isolation (`/config`)
- **Encrypted DoH Forwarders**: Preconfigured templates for Cloudflare (`doh_cloudflared.yml`) and Quad9 (`doh_quad9.yml`) listening locally on `127.0.0.1:5053`, bypassing local ISP DNS inspection.
- **Browser Hardening**: `user.js` and `browser_policies.json` force Firefox TRR Mode 3 (Strict DoH), disable WebRTC IP leaks (`media.peerconnection.enabled = false`), disable WebGL fingerprinting hooks, enable First-Party Isolation, and force complete cache/cookie wipes on browser shutdown.

### 3. Native Agent Control Channel (`/mcp`)
- Standard stdio Model Context Protocol (MCP) server (`mcp/server.py`) allowing AI agents (like Claude/Jules) or local scripts to programmatically inspect routing tables, toggle firewall killswitches, check DNS security, and manage isolated browser sessions via standard JSON-RPC 2.0.

### 4. Automated Scripts (`/scripts`)
- **`scripts/setup_firewall.sh` / `.ps1`**: Automated setup to initialize local firewall killswitch rules and clean up temporary profiles.
- **`scripts/launch_isolated_browser.sh` / `.ps1`**: One-command script to spin up a completely isolated, hardened temporary browser window and wipe all session state upon closing.

---

## 🚀 Quick Start Guide

### 1. View System Privacy Status
Run the native CLI interface:
```bash
python3 -m core.cli status
```
Or output in JSON format:
```bash
python3 -m core.cli --json status
```

### 2. Run Privacy Verification Diagnostic
Check for DNS leaks, WebRTC protection, public IP lookup, and zero-log compliance:
```bash
python3 verify_privacy.py
```

### 3. Launch an Isolated Hardened Browser Session
- **Linux**:
  ```bash
  ./scripts/launch_isolated_browser.sh
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\scripts\launch_isolated_browser.ps1
  ```

### 4. Enable Firewall Zero-Leak Killswitch
- **Linux**:
  ```bash
  sudo ./scripts/setup_firewall.sh enable wg0
  ```
- **Windows (Admin PowerShell)**:
  ```powershell
  .\scripts\setup_firewall.ps1 -Action enable -VpnInterface wg0
  ```

### 5. Drive Routing State via AI Agent / MCP Server
Start the local MCP server channel:
```bash
python3 mcp/server.py
```
Or test tool invocation using the client harness:
```bash
python3 mcp/client_test.py
```

---

## 🧪 Running Unit Tests
Execute the comprehensive test suite to confirm core modules and MCP server function as expected:
```bash
python3 -m unittest discover -s tests
```

---

## 🔒 Zero Logging & Privacy Guarantee
This application runs 100% locally on your machine.
- Zero analytics or telemetry transmitted.
- DNS logs directed to `/dev/null`.
- Ephemeral browser profile data zero-overwritten on session teardown.
- Outbound non-VPN traffic blocked when killswitch is enabled.
