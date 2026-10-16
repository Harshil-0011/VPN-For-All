"""Native Control CLI for Privacy Routing & Isolation Engine.

Lightweight, webview-free command-line interface directly inspecting tunnels,
routing rules, killswitch, and zero-log status.
"""

import sys
import json
import argparse
from typing import Any

from core.network import NetworkManager
from core.tunnel import TunnelManager
from core.firewall import FirewallManager
from core.session import SessionManager


def format_output(data: Any, json_output: bool = False) -> str:
    if json_output:
        return json.dumps(data, indent=2)
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            lines.append(f"- {item}")
        return "\n".join(lines)
    return str(data)


def main():
    parser = argparse.ArgumentParser(description="Crafting-Apps Local Privacy Routing CLI")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Interfaces & Routes
    subparsers.add_parser("network", help="Inspect local network interfaces and route state")
    subparsers.add_parser("routes", help="Show system routing table")

    # Tunnel management
    tunnel_p = subparsers.add_parser("tunnel", help="Query or manage local tunnel")
    tunnel_p.add_argument("--interface", default="wg0", help="Interface name (default: wg0)")
    tunnel_p.add_argument("--action", choices=["status", "start", "stop"], default="status")
    tunnel_p.add_argument("--config", help="Path to WireGuard configuration file")

    # Firewall & Killswitch
    fw_p = subparsers.add_parser("firewall", help="Query or toggle firewall killswitch")
    fw_p.add_argument("--action", choices=["status", "enable", "disable"], default="status")
    fw_p.add_argument("--interface", default="wg0", help="Allowed VPN interface")

    # Session Management
    sess_p = subparsers.add_parser("session", help="Manage isolated ephemeral profiles")
    sess_p.add_argument("--action", choices=["list", "create", "wipe", "wipe-all"], default="list")
    sess_p.add_argument("--name", help="Session ID / profile name")

    # Full System Overview
    subparsers.add_parser("status", help="Get full privacy routing and zero-log status")

    args = parser.parse_args()

    nm = NetworkManager()
    tm = TunnelManager()
    fm = FirewallManager()
    sm = SessionManager()

    if args.command == "network":
        res = nm.get_interfaces()
        print(format_output(res, args.json))

    elif args.command == "routes":
        res = nm.get_routing_table()
        print(format_output(res, args.json))

    elif args.command == "tunnel":
        if args.action == "status":
            res = tm.get_tunnel_status(args.interface)
        elif args.action == "start":
            if not args.config:
                print("Error: --config path is required to start tunnel.", file=sys.stderr)
                sys.exit(1)
            res = tm.start_tunnel(args.config, args.interface)
        elif args.action == "stop":
            res = tm.stop_tunnel(args.interface)
        print(format_output(res, args.json))

    elif args.command == "firewall":
        if args.action == "status":
            res = fm.get_status()
        elif args.action == "enable":
            res = fm.enable_killswitch(args.interface)
        elif args.action == "disable":
            res = fm.disable_killswitch()
        print(format_output(res, args.json))

    elif args.command == "session":
        if args.action == "list":
            res = sm.list_sessions()
        elif args.action == "create":
            res = sm.create_isolated_session(args.name)
        elif args.action == "wipe":
            if not args.name:
                print("Error: --name session ID is required for wipe action.", file=sys.stderr)
                sys.exit(1)
            res = sm.wipe_session(args.name)
        elif args.action == "wipe-all":
            res = sm.wipe_all_sessions()
        print(format_output(res, args.json))

    elif args.command == "status" or not args.command:
        full_status = {
            "network_interfaces": len(nm.get_interfaces()),
            "tunnel_status": tm.get_tunnel_status("wg0"),
            "firewall": fm.get_status(),
            "active_sessions": len(sm.list_sessions()),
            "zero_log_policy": "STRICT_LOCAL_ONLY_NO_PERSISTENT_LOGS"
        }
        print(format_output(full_status, args.json))


if __name__ == "__main__":
    main()
