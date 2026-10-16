"""Client / Test runner for local MCP server communication over stdio."""

import subprocess
import json
import os
import sys

def test_mcp_channel():
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Send initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    init_resp = json.loads(proc.stdout.readline())
    print("Initialize Response:", init_resp)

    # List tools
    list_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    proc.stdin.write(json.dumps(list_req) + "\n")
    proc.stdin.flush()
    list_resp = json.loads(proc.stdout.readline())
    print("Tools Manifest:", list_resp)

    # Call get_routing_status tool
    call_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_routing_status",
            "arguments": {}
        }
    }
    proc.stdin.write(json.dumps(call_req) + "\n")
    proc.stdin.flush()
    call_resp = json.loads(proc.stdout.readline())
    print("Tool Call Result:", call_resp)

    proc.terminate()

if __name__ == "__main__":
    test_mcp_channel()
