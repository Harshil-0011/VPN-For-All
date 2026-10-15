"""Local Web Server & REST API Backend for Privacy Routing Control UI.

Runs entirely on http://127.0.0.1:8080 (loopback only) with zero remote tracking or telemetry.
Provides REST API endpoints for the web UI/App to control firewall killswitch, inspect network,
query tunnels, and launch or wipe ephemeral browser profiles.
"""

import sys
import os
import json
import http.server
import socketserver
import urllib.parse
from typing import Dict, Any

# Path resolution for core imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.network import NetworkManager
from core.tunnel import TunnelManager
from core.firewall import FirewallManager
from core.session import SessionManager


class PrivacyAPIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving web UI assets and REST API endpoints."""

    nm = NetworkManager()
    tm = TunnelManager()
    fm = FirewallManager()
    sm = SessionManager()

    def __init__(self, *args, **kwargs):
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        super().__init__(*args, directory=static_dir, **kwargs)

    def _send_json_response(self, data: Any, status_code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # REST API Routes
        if path == "/api/status":
            status = {
                "interfaces": self.nm.get_interfaces(),
                "routes": self.nm.get_routing_table(),
                "tunnel": self.tm.get_tunnel_status("wg0"),
                "firewall": self.fm.get_status(),
                "sessions": self.sm.list_sessions(),
                "zero_log": True
            }
            self._send_json_response(status)

        elif path == "/api/interfaces":
            self._send_json_response(self.nm.get_interfaces())

        elif path == "/api/routes":
            self._send_json_response(self.nm.get_routing_table())

        elif path == "/api/firewall":
            self._send_json_response(self.fm.get_status())

        elif path == "/api/sessions":
            self._send_json_response(self.sm.list_sessions())

        else:
            # Fallback to static frontend assets (index.html, app.js, style.css)
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            payload = {}

        if path == "/api/firewall/toggle":
            enable = payload.get("enable", True)
            iface = payload.get("interface", "wg0")
            if enable:
                res = self.fm.enable_killswitch(iface)
            else:
                res = self.fm.disable_killswitch()
            self._send_json_response(res)

        elif path == "/api/session/create":
            name = payload.get("name")
            res = self.sm.create_isolated_session(name)
            self._send_json_response(res)

        elif path == "/api/session/wipe":
            session_id = payload.get("session_id")
            if not session_id:
                self._send_json_response({"error": "Missing session_id"}, 400)
            else:
                res = self.sm.wipe_session(session_id)
                self._send_json_response(res)

        elif path == "/api/session/wipe-all":
            res = self.sm.wipe_all_sessions()
            self._send_json_response(res)

        elif path == "/api/tunnel/start":
            config_path = payload.get("config")
            iface = payload.get("interface", "wg0")
            res = self.tm.start_tunnel(config_path, iface)
            self._send_json_response(res)

        elif path == "/api/tunnel/stop":
            iface = payload.get("interface", "wg0")
            res = self.tm.stop_tunnel(iface)
            self._send_json_response(res)

        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)


def run_server(port: int = 8080):
    host = "127.0.0.1"
    server_address = (host, port)
    httpd = socketserver.TCPServer(server_address, PrivacyAPIHandler)
    print(f"======================================================================")
    print(f" [Crafting-Apps] Privacy Routing Web App active at: http://{host}:{port}")
    print(f"======================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Web server shut down.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
