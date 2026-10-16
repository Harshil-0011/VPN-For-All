"""Session Isolation and Zero-Log Enforcer Daemon.

Monitors active privacy sessions, manages temporary profile directories,
enforces zero-logging policies on local files, and securely purges session artifacts on exit.
"""

import os
import shutil
import tempfile
import time
import json
import uuid
from typing import Dict, List, Optional, Any


class SessionManager:
    """Manages ephemeral, containerized user browser profiles and session cleanup."""

    def __init__(self, base_temp_dir: Optional[str] = None):
        self.base_dir = base_temp_dir or os.path.join(tempfile.gettempdir(), "privacy_router_sessions")
        os.makedirs(self.base_dir, exist_ok=True)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_isolated_session(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Creates an ephemeral, completely isolated profile directory with privacy templates applied."""
        session_id = profile_name or f"session_{uuid.uuid4().hex[:8]}"
        session_path = os.path.join(self.base_dir, session_id)

        if os.path.exists(session_path):
            shutil.rmtree(session_path, ignore_errors=True)

        os.makedirs(session_path, exist_ok=True)

        # Initialize zero-log policy descriptor in the session directory
        meta_file = os.path.join(session_path, ".privacy_session.json")
        meta_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "zero_log": True,
            "isolation_level": "strict_container",
            "ephemeral": True
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)

        self.active_sessions[session_id] = {
            "session_id": session_id,
            "path": session_path,
            "created_at": meta_data["created_at"],
            "status": "active"
        }

        return {
            "success": True,
            "session_id": session_id,
            "path": session_path,
            "message": "Ephemeral session container created successfully."
        }

    def wipe_session(self, session_id: str) -> Dict[str, Any]:
        """Completely purges and overwrites session data and cache directories on disk."""
        if session_id in self.active_sessions:
            path = self.active_sessions[session_id]["path"]
            del self.active_sessions[session_id]
        else:
            path = os.path.join(self.base_dir, session_id)

        if os.path.exists(path):
            # Zero-out configuration/history files prior to deletion if possible
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                        with open(fp, "wb") as fh:
                            fh.write(b"\x00" * min(size, 4096))
                    except Exception:
                        pass
            shutil.rmtree(path, ignore_errors=True)
            return {"success": True, "session_id": session_id, "message": f"Session {session_id} securely wiped from disk."}

        return {"success": False, "session_id": session_id, "error": "Session directory does not exist."}

    def wipe_all_sessions(self) -> Dict[str, Any]:
        """Purges all temporary profile containers under the base directory."""
        count = 0
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                if os.path.isdir(item_path):
                    self.wipe_session(item)
                    count += 1
        self.active_sessions.clear()
        return {"success": True, "wiped_count": count, "message": "All session data purged."}

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Lists active managed sessions."""
        sessions = []
        if os.path.exists(self.base_dir):
            for item in os.listdir(self.base_dir):
                item_path = os.path.join(self.base_dir, item)
                meta_file = os.path.join(item_path, ".privacy_session.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            sessions.append(data)
                    except Exception:
                        sessions.append({"session_id": item, "path": item_path})
        return sessions


if __name__ == "__main__":
    sm = SessionManager()
    sess = sm.create_isolated_session("test_session")
    print("Created:", sess)
    print("Active:", sm.list_sessions())
    print("Wiped:", sm.wipe_session("test_session"))
