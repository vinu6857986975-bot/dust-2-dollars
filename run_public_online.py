# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Global Public Multi-Device Deployment Launcher
Runs the DUST 2 DOLLAR backend and creates a secure global public tunnel
accessible from any smartphone, tablet, laptop, or computer worldwide.
"""

import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import re
import socket
import subprocess
import threading

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "dead-stock-agent")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def find_cloudflared():
    paths = [
        os.path.join(ROOT_DIR, "cloudflared.exe"),
        os.path.join(APP_DIR, "cloudflared.exe"),
        "cloudflared.exe",
        "cloudflared"
    ]
    for p in paths:
        if os.path.isfile(p):
            return os.path.abspath(p)
    return None

def main():
    print("=" * 70)
    print("  DUST 2 DOLLAR - Global Public Multi-Device Deployment")
    print("  Autonomous Multi-Agent AI Capital Recovery Platform")
    print("=" * 70)
    print()

    cloudflared_bin = find_cloudflared()
    if not cloudflared_bin:
        print("[!] Error: cloudflared.exe was not found. Please ensure cloudflared is present.")
        sys.exit(1)

    # Start local Python server
    print("  [1/2] Starting DUST 2 DOLLAR Python Server on port 8001...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=APP_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait 1.5s for server to start
    time.sleep(1.5)

    # Start Cloudflare Tunnel
    print("  [2/2] Launching Global Cloudflare Public Tunnel...")
    cf_cmd = [
        cloudflared_bin,
        "tunnel",
        "--url", "http://127.0.0.1:8001",
        "--no-autoupdate"
    ]

    cf_process = subprocess.Popen(
        cf_cmd,
        cwd=APP_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Read tunnel output to capture the public URL
    def monitor_tunnel():
        nonlocal public_url
        for line in cf_process.stderr:
            match = url_pattern.search(line)
            if match and not public_url:
                public_url = match.group(0)

    monitor_thread = threading.Thread(target=monitor_tunnel, daemon=True)
    monitor_thread.start()

    # Wait up to 25 seconds for the URL
    timeout = 25
    start_t = time.time()
    while not public_url and (time.time() - start_t) < timeout:
        time.sleep(0.5)

    local_ip = get_local_ip()

    print()
    print("  " + "=" * 66)
    print("  |         DUST 2 DOLLAR IS NOW LIVE FOR ANY DEVICE!            |")
    print("  " + "=" * 66)
    if public_url:
        print("  |  GLOBAL PUBLIC URL (Any Phone / Laptop / Tablet Worldwide):  |")
        print(f"  |  >> {public_url:<56} |")
        print("  |                                                                |")
    else:
        print("  |  [!] Tunnel URL taking longer to resolve.                      |")

    print("  |  LOCAL WI-FI URL (Same Wi-Fi Network):                         |")
    print(f"  |  >> http://{local_ip}:8001{' ' * max(0, 49 - len(local_ip))} |")
    print("  |                                                                |")
    print("  |  LOCALHOST (This Machine):                                     |")
    print("  |  >> http://localhost:8001                                      |")
    print("  " + "=" * 66)
    print()
    print("  >> Send the GLOBAL PUBLIC URL to anyone or open it on your phone!")
    print("  Press Ctrl+C anytime to stop.")
    print()

    # Save to file for easy copy
    if public_url:
        with open(os.path.join(ROOT_DIR, "PUBLIC_URL.txt"), "w", encoding="utf-8") as f:
            f.write("DUST 2 DOLLAR - LIVE ACCESS URLS\n")
            f.write(f"Global Public URL (Any Device): {public_url}\n")
            f.write(f"Local Wi-Fi Network URL:        http://{local_ip}:8001\n")
            f.write("Localhost URL:                  http://localhost:8001\n")

    try:
        while True:
            time.sleep(1)
            if server_process.poll() is not None:
                print("[!] Local server exited.")
                break
            if cf_process.poll() is not None:
                print("[!] Cloudflare tunnel exited.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        try:
            server_process.terminate()
        except Exception:
            pass
        try:
            cf_process.terminate()
        except Exception:
            pass
        print("DUST 2 DOLLAR stopped cleanly.")

if __name__ == "__main__":
    main()
