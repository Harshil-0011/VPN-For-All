# Contributing to VPN For All

Thank you for your interest in contributing to **VPN For All**! We welcome contributions to enhance local privacy routing, firewall killswitch capabilities, anti-fingerprinting browser templates, and MCP agent channels.

## Principles & Core Commitments
1. **Local-First & Zero Logging**: Code must run 100% locally. Never add external analytics, third-party tracking, or remote database logging.
2. **Native Performance**: Avoid adding heavy webviews or external framework dependencies. Keep native execution lightweight and portable.
3. **Cross-Platform Compatibility**: Always verify changes on both Linux (`iptables`/`nftables`) and Windows (`netsh`).

## How to Contribute
1. Fork the repository on GitHub.
2. Create a topic branch: `git checkout -b feature/my-new-feature`.
3. Ensure all tests pass: `python3 -m unittest discover -s tests`.
4. Run the privacy verification script: `python3 verify_privacy.py`.
5. Submit a Pull Request.

## Security & Leak Reporting
If you discover a DNS leak, WebRTC leak, or unhandled outbound traffic path, please open an issue or report it directly to the maintainers.
