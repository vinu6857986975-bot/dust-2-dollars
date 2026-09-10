# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR Root Launcher
Executes the DUST 2 DOLLAR Dead-Stock Decision Agent platform from workspace root.
"""
import os
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "dead-stock-agent")

if not os.path.exists(APP_DIR):
    print(f"Error: dead-stock-agent directory not found at {APP_DIR}")
    sys.exit(1)

print("=" * 65)
print("  💰 DUST 2 DOLLARS — Autonomous Retail Dead-Stock Decision Agent")
print("  Autonomous Multi-Agent AI Capital Recovery Platform")
print("=" * 65)
print(f"Starting server in: {APP_DIR}")
print("Opening http://localhost:8001 ...\n")

os.chdir(APP_DIR)
sys.path.insert(0, APP_DIR)
import server
server.init_db()

local_ip = server.get_local_ip()
server_instance = server.http.server.HTTPServer(("0.0.0.0", server.PORT), server.Dust2DollarHandler)
print()
print("  ╔═════════════════════════════════════════════════════════════╗")
print("  ║        💰 DUST 2 DOLLARS — AI DECISION PLATFORM             ║")
print("  ║        Autonomous Retail Capital Recovery Engine            ║")
print("  ╠═════════════════════════════════════════════════════════════╣")
print(f"  ║   Local Web:   http://localhost:{server.PORT}                      ║")
print(f"  ║   Network:     http://{local_ip}:{server.PORT}                 ║")
print("  ╠═════════════════════════════════════════════════════════════╣")
print("  ║   Press Ctrl+C to stop                                      ║")
print("  ╚═════════════════════════════════════════════════════════════╝")
print()

try:
    server_instance.serve_forever()
except KeyboardInterrupt:
    print("\n  [Dust 2 Dollar] Server stopped.")
    server_instance.server_close()
