# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Root Server Launcher
Executes the DUST 2 DOLLAR Autonomous Dead-Stock Decision Agent from workspace root.
Port: 8001
"""
import os
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "dead-stock-agent")

if not os.path.exists(APP_DIR):
    print(f"Error: dead-stock-agent directory not found at {APP_DIR}")
    sys.exit(1)

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)

import server

if __name__ == "__main__":
    server.init_db()
    local_ip = server.get_local_ip()
    print("=" * 68)
    print("  💰 DUST 2 DOLLAR — Business Dead-Stock Decision Agent")
    print("  Autonomous Multi-Agent AI Capital Recovery Platform")
    print("=" * 68)
    print(f"  Local Web:   http://localhost:{server.PORT}")
    print(f"  Network:     http://{local_ip}:{server.PORT}")
    print("=" * 68)
    print("  Ready! Press Ctrl+C to stop.\n")

    server_instance = server.http.server.HTTPServer(("0.0.0.0", server.PORT), server.Dust2DollarHandler)
    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        print("\n[Dust 2 Dollar] Server stopped.")
        server_instance.server_close()
