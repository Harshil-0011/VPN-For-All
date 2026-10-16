"""Unit tests for local MCP server tools and JSON-RPC dispatching."""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server import LocalMCPServer


class TestMCPServer(unittest.TestCase):

    def setUp(self):
        self.server = LocalMCPServer()

    def test_initialize(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 1)
        self.assertIn("serverInfo", resp["result"])

    def test_tools_list(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        resp = self.server.handle_request(req)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("get_routing_status", tool_names)
        self.assertIn("toggle_killswitch", tool_names)
        self.assertIn("manage_session", tool_names)

    def test_tool_call_get_routing_status(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_routing_status",
                "arguments": {}
            }
        }
        resp = self.server.handle_request(req)
        self.assertIn("result", resp)
        self.assertEqual(resp["id"], 3)


if __name__ == "__main__":
    unittest.main()
