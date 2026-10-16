"""Unit tests for app REST API server."""

import unittest
import urllib.request
import json
import threading
import time
import socket
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.server import PrivacyAPIHandler, socketserver


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class TestAppServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.port = find_free_port()
        cls.httpd = socketserver.TCPServer(("127.0.0.1", cls.port), PrivacyAPIHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_get_status(self):
        url = f"http://127.0.0.1:{self.port}/api/status"
        req = urllib.request.urlopen(url)
        self.assertEqual(req.getcode(), 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("interfaces", data)
        self.assertIn("firewall", data)
        self.assertTrue(data.get("zero_log"))

    def test_toggle_firewall(self):
        url = f"http://127.0.0.1:{self.port}/api/firewall/toggle"
        req_data = json.dumps({"enable": False, "interface": "wg0"}).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.getcode(), 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data.get("success"))

if __name__ == "__main__":
    unittest.main()
