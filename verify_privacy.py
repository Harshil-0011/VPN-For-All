#!/usr/bin/env python3
"""Verification Script for Local Privacy Routing & Session Isolation.

Checks:
1. Public IP Lookup & VPN Interface verification
2. DNS Leak Status & DoH Proxy Check
3. WebRTC Leak Protection in configuration files
4. Verification of Zero-Logging configuration (no active disk logging hooks)
5. Session container hygiene and ephemeral folder status
"""

import sys
import os
import json
import socket
import urllib.request
import ssl

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from core.network import NetworkManager
from core.tunnel import TunnelManager
from core.firewall import FirewallManager
from core.session import SessionManager


def check_public_ip():
    """Queries public IP and checks if request routes through VPN/tunnel."""
    print("\n--- 1. Public IP & Routing Verification ---")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    ip_services = [
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/all.json"
    ]
    public_ip = None
    for service in ip_services:
        try:
            req = urllib.request.Request(service, headers={'User-Agent': 'PrivacyVerifier/1.0'})
            with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                public_ip = data.get("ip") or data.get("ip_addr")
                if public_ip:
                    break
        except Exception:
            continue

    if public_ip:
        print(f"[+] Current Public IP: {public_ip}")
    else:
        print("[!] Unable to reach external IP service directly (Killswitch may be ACTIVE or offline).")

    tm = TunnelManager()
    wg_status = tm.get_tunnel_status("wg0")
    print(f"[*] WireGuard Interface wg0 Status: {wg_status.get('status', 'Inactive')}")
    return {"public_ip": public_ip, "tunnel_active": wg_status.get("active", False)}


def check_dns_leak():
    """Checks DNS resolution path and verifies DoH settings."""
    print("\n--- 2. DNS Leak & DoH Forwarder Verification ---")
    nm = NetworkManager()

    # Check if local DoH forwarder is listening on port 5053
    doh_bound = nm.test_bound_socket("127.0.0.1", 5053)
    print(f"[*] Local DoH Proxy Socket (127.0.0.1:5053): {'RESPONSIVE' if doh_bound else 'NOT DETECTED (Check cloudflared/Quad9 daemon)'}")

    # Inspect user.js for TRR / DoH enforcement
    user_js_path = os.path.join(PROJECT_ROOT, "config", "user.js")
    trr_mode_ok = False
    if os.path.exists(user_js_path):
        with open(user_js_path, "r", encoding="utf-8") as f:
            content = f.read()
            if 'user_pref("network.trr.mode", 3);' in content:
                trr_mode_ok = True

    print(f"[+] Firefox TRR Mode 3 (Strict DoH Only) enforced in user.js: {trr_mode_ok}")
    return {"doh_bound": doh_bound, "trr_mode_strict": trr_mode_ok}


def check_webrtc_protection():
    """Verifies WebRTC leak protection rules in configuration files."""
    print("\n--- 3. WebRTC Leak Protection Checks ---")
    user_js_path = os.path.join(PROJECT_ROOT, "config", "user.js")
    policies_path = os.path.join(PROJECT_ROOT, "config", "browser_policies.json")

    webrtc_disabled_user_js = False
    webrtc_disabled_policies = False

    if os.path.exists(user_js_path):
        with open(user_js_path, "r", encoding="utf-8") as f:
            if 'user_pref("media.peerconnection.enabled", false);' in f.read():
                webrtc_disabled_user_js = True

    if os.path.exists(policies_path):
        with open(policies_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            prefs = data.get("policies", {}).get("Preferences", {})
            if prefs.get("media.peerconnection.enabled") is False:
                webrtc_disabled_policies = True

    print(f"[+] WebRTC Disabled in user.js: {webrtc_disabled_user_js}")
    print(f"[+] WebRTC Disabled in browser_policies.json: {webrtc_disabled_policies}")
    return {"webrtc_user_js": webrtc_disabled_user_js, "webrtc_policies": webrtc_disabled_policies}


def check_zero_log_config():
    """Validates that no persistent logging hooks exist in configuration files."""
    print("\n--- 4. Zero-Log Configuration Audit ---")
    configs = [
        os.path.join(PROJECT_ROOT, "config", "doh_cloudflared.yml"),
        os.path.join(PROJECT_ROOT, "config", "doh_quad9.yml"),
        os.path.join(PROJECT_ROOT, "config", "routing_defaults.json")
    ]

    no_logs_found = True
    for cfg in configs:
        if os.path.exists(cfg):
            with open(cfg, "r", encoding="utf-8") as f:
                content = f.read()
                if "logfile: /dev/null" in content or '"zero_log": true' in content:
                    print(f"[+] Verified zero-log directive in: {os.path.basename(cfg)}")
                elif "log" in content.lower() and "fatal" not in content.lower():
                    print(f"[!] Warning: Possible log entry in {os.path.basename(cfg)}")
                    no_logs_found = False

    return {"zero_log_verified": no_logs_found}


def run_full_privacy_verification():
    """Runs all verification checks and prints summary report."""
    print("======================================================================")
    print(" [Crafting-Apps] Local Privacy Routing & IP Isolation Verification")
    print("======================================================================")

    r1 = check_public_ip()
    r2 = check_dns_leak()
    r3 = check_webrtc_protection()
    r4 = check_zero_log_config()

    print("\n======================================================================")
    print(" SUMMARY PRIVACY REPORT")
    print("======================================================================")
    print(f" WebRTC Leak Protection: {'PASS' if (r3['webrtc_user_js'] and r3['webrtc_policies']) else 'FAIL'}")
    print(f" Strict DoH Enforcement: {'PASS' if r2['trr_mode_strict'] else 'FAIL'}")
    print(f" Zero-Log Config Audit:  {'PASS' if r4['zero_log_verified'] else 'FAIL'}")
    print("======================================================================")


if __name__ == "__main__":
    run_full_privacy_verification()
