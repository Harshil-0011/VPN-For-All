"""Local Network Interface, Socket, and Routing Table Manager.

Handles local interface enumeration, socket test bindings, and routing table abstractions
for Windows and Linux without transmitting telemetry or logs.
"""

import os
import platform
import socket
import subprocess
import json
from typing import Dict, List, Optional, Any


class NetworkManager:
    """Manages local network interfaces, socket bindings, and route inspection."""

    def __init__(self):
        self.os_type = platform.system().lower()

    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Enumerates local network interfaces across platforms."""
        interfaces = []
        if self.os_type == "linux":
            try:
                out = subprocess.check_output(["ip", "-j", "addr"], text=True)
                data = json.loads(out)
                for iface in data:
                    name = iface.get("ifname")
                    addrs = []
                    for addr in iface.get("addr_info", []):
                        addrs.append(addr.get("local"))
                    interfaces.append({
                        "name": name,
                        "type": "loopback" if name == "lo" else "ethernet/wifi",
                        "addresses": addrs,
                        "state": iface.get("operstate", "UNKNOWN").lower()
                    })
            except Exception:
                # Fallback via socket
                interfaces = self._fallback_interfaces()
        elif self.os_type == "windows":
            try:
                cmd = ["powershell", "-NoProfile", "-Command", "Get-NetIPAddress | Select-Object InterfaceAlias, IPAddress | ConvertTo-Json"]
                out = subprocess.check_output(cmd, text=True)
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                iface_map: Dict[str, List[str]] = {}
                for item in data:
                    alias = item.get("InterfaceAlias")
                    ip = item.get("IPAddress")
                    if alias and ip:
                        iface_map.setdefault(alias, []).append(ip)
                for alias, ips in iface_map.items():
                    interfaces.append({
                        "name": alias,
                        "type": "ethernet/wifi",
                        "addresses": ips,
                        "state": "up"
                    })
            except Exception:
                interfaces = self._fallback_interfaces()
        else:
            interfaces = self._fallback_interfaces()
        return interfaces

    def _fallback_interfaces(self) -> List[Dict[str, Any]]:
        """Fallback interface enumeration using Python standard sockets."""
        hostname = socket.gethostname()
        try:
            addrs = socket.gethostbyname_ex(hostname)[2]
        except Exception:
            addrs = ["127.0.0.1"]
        return [{
            "name": "default",
            "type": "generic",
            "addresses": addrs,
            "state": "up"
        }]

    def get_routing_table(self) -> List[Dict[str, str]]:
        """Inspects active system routing table."""
        routes = []
        if self.os_type == "linux":
            try:
                out = subprocess.check_output(["ip", "route", "show"], text=True)
                for line in out.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split()
                    routes.append({
                        "destination": parts[0] if parts else "unknown",
                        "raw": line
                    })
            except Exception as e:
                routes.append({"destination": "error", "raw": str(e)})
        elif self.os_type == "windows":
            try:
                out = subprocess.check_output(["route", "print"], text=True)
                for line in out.split("\n"):
                    line_s = line.strip()
                    if line_s.startswith("0.0.0.0") or line_s.startswith("127."):
                        routes.append({"destination": line_s.split()[0], "raw": line_s})
            except Exception as e:
                routes.append({"destination": "error", "raw": str(e)})
        else:
            routes.append({"destination": "unsupported", "raw": "Platform not supported for detailed route print"})
        return routes

    def test_bound_socket(self, target_host: str = "1.1.1.1", target_port: int = 53, timeout: float = 2.0) -> bool:
        """Tests outbound socket connection capability without sending identifying payloads."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        try:
            s.connect((target_host, target_port))
            s.close()
            return True
        except Exception:
            return False


if __name__ == "__main__":
    nm = NetworkManager()
    print("Interfaces:", nm.get_interfaces())
    print("Routes:", nm.get_routing_table())
