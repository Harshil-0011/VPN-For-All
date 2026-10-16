"""Unit tests for Core Engine modules (Network, Tunnel, Firewall, Session, CLI)."""

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.network import NetworkManager
from core.tunnel import TunnelManager
from core.firewall import FirewallManager
from core.session import SessionManager


class TestCoreEngine(unittest.TestCase):

    def test_network_manager(self):
        nm = NetworkManager()
        interfaces = nm.get_interfaces()
        self.assertIsInstance(interfaces, list)
        self.assertGreater(len(interfaces), 0)

        routes = nm.get_routing_table()
        self.assertIsInstance(routes, list)

    def test_tunnel_manager(self):
        tm = TunnelManager()
        status = tm.get_tunnel_status("wg0")
        self.assertIn("interface", status)
        self.assertEqual(status["interface"], "wg0")

    def test_firewall_manager(self):
        fm = FirewallManager()
        status = fm.get_status()
        self.assertIn("killswitch_active", status)
        self.assertIn("os", status)

    def test_session_manager(self):
        sm = SessionManager()
        sess = sm.create_isolated_session("unittest_session")
        self.assertTrue(sess["success"])
        self.assertEqual(sess["session_id"], "unittest_session")

        sessions = sm.list_sessions()
        self.assertTrue(any(s["session_id"] == "unittest_session" for s in sessions))

        wipe = sm.wipe_session("unittest_session")
        self.assertTrue(wipe["success"])


if __name__ == "__main__":
    unittest.main()
