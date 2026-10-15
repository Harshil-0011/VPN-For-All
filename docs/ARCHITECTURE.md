# Crafting-Apps Architecture & Zero-Log Architecture Guide

## Overview & Philosophy
This application follows the **Crafting Apps** architectural philosophy:
- **Native Execution**: Zero heavy web-view or Electron bloat. Direct native system interactions via python/shell.
- **Local-First & Zero Paid External Dependencies**: All routing decisions, DNS queries, firewall rules, and profiles run locally on your PC.
- **Agent/MCP Ready**: Built-in stdio Model Context Protocol server exposing control capabilities to AI coding agents and automation engines.
- **Zero-Log Assurance**: Strict enforced no-log configuration directives (`logfile: /dev/null`, ephemeral profiles, wipe-on-exit).

## Architecture Components

```
+-----------------------------------------------------------------------+
|                       LOCAL USER / AI AGENT                           |
|      (CLI: python3 -m core.cli | MCP Server: python3 mcp/server.py)    |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      CORE ENGINE CONTROLLERS                          |
|  - NetworkManager  (core/network.py)  : Interface & Route Inspection  |
|  - TunnelManager   (core/tunnel.py)   : WireGuard / TUN Interface     |
|  - FirewallManager (core/firewall.py) : Killswitch (netsh/iptables)  |
|  - SessionManager  (core/session.py)  : Ephemeral Profiles & Cleanup  |
+-----------------------------------+-----------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
+-----------------------------------+   +-----------------------------------+
|     SYSTEM FIREWALL & KILLSWITCH  |   |    CONTAINERIZED BROWSER PROFILE  |
|  - Linux: iptables / nftables     |   |  - Firefox / Mullvad Browser      |
|  - Windows: netsh advfirewall     |   |  - Anti-Fingerprinting (user.js)  |
|  - Blocks unencrypted leak path   |   |  - WebRTC Leak Protection         |
+-----------------------------------+   +-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                   LOCAL DoH ENCRYPTED DNS FORWARDER                   |
|  - Cloudflared / Quad9 proxy on 127.0.0.1:5053                        |
|  - Encrypted DoH outbound queries (1.1.1.1 / 9.9.9.9)                 |
|  - Local ISP cannot inspect domain queries                            |
+-----------------------------------------------------------------------+
```

## Zero-Log & IP Isolation Verification

To verify IP isolation and zero persistent logging on your machine:

1. **Run Diagnostic Script**:
   ```bash
   python3 verify_privacy.py
   ```
2. **Verify Firewall Rules**:
   - Linux: `sudo iptables -L -v -n`
   - Windows: `netsh advfirewall firewall show rule name=LocalPrivacyKillswitchBlockAll`
3. **Inspect Active Session Folder**:
   - Ephemeral profiles reside in `/tmp/privacy_router_sessions/` or `%TEMP%\privacy_router_sessions\`.
   - Each session is zero-overwritten and deleted on process completion.
