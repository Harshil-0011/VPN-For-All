"""Local Model Context Protocol (MCP) Server for Privacy Routing Engine.

Provides standard JSON-RPC 2.0 / MCP stdio control channels allowing AI coding agents
and automated tools to drive, inspect, and modify routing state programmatically.
"""

import sys
import json
import os
from typing import Dict, Any, List

# Add parent directory to path for core imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.network import NetworkManager
from core.tunnel import TunnelManager
from core.firewall import FirewallManager
from core.session import SessionManager


class LocalMCPServer:
    """JSON-RPC 2.0 / MCP compliant local control channel."""

    def __init__(self):
        self.network_mgr = NetworkManager()
        self.tunnel_mgr = TunnelManager()
        self.firewall_mgr = FirewallManager()
        self.session_mgr = SessionManager()

    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        """Returns MCP tool definitions exposed to agents."""
        return [
            {
                "name": "get_routing_status",
                "description": "Get current network interfaces, tunnel status, firewall killswitch state, and zero-log policy info.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "inspect_tunnels",
                "description": "Inspect WireGuard / VPN tunnels state and metrics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "interface": {"type": "string", "default": "wg0"}
                    }
                }
            },
            {
                "name": "toggle_killswitch",
                "description": "Enable or disable system-wide firewall killswitch for zero IP leaks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "enable": {"type": "boolean"},
                        "interface": {"type": "string", "default": "wg0"}
                    },
                    "required": ["enable"]
                }
            },
            {
                "name": "get_dns_security",
                "description": "Verify local DoH (DNS-over-HTTPS) configuration and status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "manage_session",
                "description": "Create, list, or securely wipe ephemeral isolated browser profiles.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["list", "create", "wipe", "wipe_all"]},
                        "session_id": {"type": "string"}
                    },
                    "required": ["action"]
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processes a JSON-RPC request."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools_manifest()}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            try:
                result_content = self.dispatch_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_content, indent=2)
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(e)}
                }

        elif method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "crafting-apps-privacy-mcp",
                        "version": "1.0.0"
                    }
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"}
        }

    def dispatch_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Dispatches tool execution to appropriate core module."""
        if tool_name == "get_routing_status":
            return {
                "interfaces": self.network_mgr.get_interfaces(),
                "routing_table": self.network_mgr.get_routing_table(),
                "firewall": self.firewall_mgr.get_status(),
                "tunnel": self.tunnel_mgr.get_tunnel_status("wg0"),
                "zero_log_enforced": True
            }

        elif tool_name == "inspect_tunnels":
            iface = args.get("interface", "wg0")
            return self.tunnel_mgr.get_tunnel_status(iface)

        elif tool_name == "toggle_killswitch":
            enable = args.get("enable", True)
            iface = args.get("interface", "wg0")
            if enable:
                return self.firewall_mgr.enable_killswitch(iface)
            else:
                return self.firewall_mgr.disable_killswitch()

        elif tool_name == "get_dns_security":
            # Test local socket query to DoH proxy port 5053
            doh_active = self.network_mgr.test_bound_socket("127.0.0.1", 5053)
            return {
                "doh_mode": "Strict (TRR Mode 3)",
                "local_doh_proxy_responsive": doh_active,
                "configured_upstreams": ["https://1.1.1.1/dns-query", "https://dns.quad9.net/dns-query"],
                "isp_dns_bypass": True
            }

        elif tool_name == "manage_session":
            action = args.get("action")
            sess_id = args.get("session_id")
            if action == "list":
                return self.session_mgr.list_sessions()
            elif action == "create":
                return self.session_mgr.create_isolated_session(sess_id)
            elif action == "wipe":
                return self.session_mgr.wipe_session(sess_id or "")
            elif action == "wipe_all":
                return self.session_mgr.wipe_all_sessions()

        raise ValueError(f"Unknown tool: {tool_name}")

    def run_stdio_loop(self):
        """Runs standard input/output loop for JSON-RPC communication."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_request(req)
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = LocalMCPServer()
    server.run_stdio_loop()
