"""PyInstaller Executable Build Script for VPN For All (Windows & Linux).

Generates standalone standalone single-file executables (.exe on Windows, standalone binary on Linux)
containing the core engine, web control app, and static dashboard assets.
"""

import sys
import os
import subprocess
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def build():
    print("======================================================================")
    print(" [Crafting-Apps] Building Standalone Executable Binary")
    print("======================================================================")

    # Check for PyInstaller
    if not shutil.which("pyinstaller"):
        print("[!] PyInstaller is not installed. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    build_dir = os.path.join(PROJECT_ROOT, "build")

    main_script = os.path.join(PROJECT_ROOT, "app", "launcher.py")
    static_folder = os.path.join(PROJECT_ROOT, "app", "static")
    config_folder = os.path.join(PROJECT_ROOT, "config")

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--name=VPN-For-All",
        f"--add-data={static_folder}{os.pathsep}app/static",
        f"--add-data={config_folder}{os.pathsep}config",
        main_script
    ]

    print(f"[*] Running PyInstaller build command: {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=PROJECT_ROOT)

    print(f"\n[+] Executable build complete! Output located at: {dist_dir}/VPN-For-All")

if __name__ == "__main__":
    build()
