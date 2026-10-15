"""Desktop App Launcher & Webview Wrapper for VPN For All."""

import sys
import os
import webbrowser
import time
import threading

# Add root directory to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.server import run_server

def main():
    port = 8080
    print("[*] Starting VPN For All Local Control Backend...")

    # Start web server in background thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    time.sleep(1)
    url = f"http://127.0.0.1:{port}"
    print(f"[+] Opening local app window at {url}...")
    webbrowser.open(url)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down app...")

if __name__ == "__main__":
    main()
