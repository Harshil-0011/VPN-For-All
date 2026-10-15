#!/usr/bin/env bash
# Launch script for Linux GUI desktop app
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
python3 -m app.launcher
