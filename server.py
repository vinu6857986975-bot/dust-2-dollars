"""
ParkFlow - Parking Management System Server
Uses only Python 3 standard library (http.server, sqlite3, json).
Zero pip dependencies required.
"""

import http.server
import json
import os
import socket
import sqlite3
import sys
import urllib.parse
from datetime import datetime
import math

PORT = 8000
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parking.db")
WEB_DIR = os.path.dirname(os.path.abspath(__file__))


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"



def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rates (
        vehicle_type TEXT PRIMARY KEY,
        base_rate REAL,
        hourly_rate REAL,
        daily_max REAL,
        ev_surcharge REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        id TEXT PRIMARY KEY,
        floor TEXT,
        slot_number INTEGER,
        type TEXT, -- Two-Wheeler, Car, SUV, EV, Priority
        is_occupied INTEGER DEFAULT 0,
        current_vehicle_id TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        plate_number TEXT,
        vehicle_type TEXT,
        driver_name TEXT,
        driver_phone TEXT,
        slot_id TEXT,
        entry_time TEXT,
        exit_time TEXT,
        duration_minutes INTEGER,
        total_amount REAL,
        payment_method TEXT,
        status TEXT -- 'active', 'completed', 'cancelled'
    )
    """)

    # Seed default rates if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM rates")
    if cursor.fetchone()["cnt"] == 0:
        rates = [
            ("Two-Wheeler", 1.0, 1.5, 12.0, 0.0),
            ("Car", 2.5, 3.0, 25.0, 0.0),
            ("SUV", 3.5, 4.0, 35.0, 0.0),
            ("EV", 3.0, 3.5, 30.0, 4.0),
            ("Priority", 2.0, 2.5, 20.0, 0.0),
        ]
        cursor.executemany("INSERT INTO rates VALUES (?, ?, ?, ?, ?)", rates)

    # Seed default slots if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM slots")
    if cursor.fetchone()["cnt"] == 0:
        slots = []
        # Level 1 (Ground Floor - 20 slots)
        for i in range(1, 7):
            slots.append((f"L1-B{i:02d}", "Level 1", i, "Two-Wheeler", 0, None))
        for i in range(7, 17):
            slots.append((f"L1-C{i:02d}", "Level 1", i, "Car", 0, None))
        for i in range(17, 21):
            slots.append((f"L1-S{i:02d}", "Level 1", i, "SUV", 0, None))

        # Level 2 (Basement B1 - 20 slots)
        for i in range(1, 13):
            slots.append((f"B1-C{i:02d}", "Basement B1", i, "Car", 0, None))
        for i in range(13, 19):
            slots.append((f"B1-S{i:02d}", "Basement B1", i, "SUV", 0, None))
        for i in range(19, 21):
            slots.append((f"B1-P{i:02d}", "Basement B1", i, "Priority", 0, None))

        # Level 3 (EV & VIP Hub - 16 slots)
        for i in range(1, 9):
            slots.append((f"L3-EV{i:02d}", "Level 3 (EV Hub)", i, "EV", 0, None))
        for i in range(9, 15):
            slots.append((f"L3-C{i:02d}", "Level 3 (EV Hub)", i, "Car", 0, None))
        for i in range(15, 17):
            slots.append((f"L3-P{i:02d}", "Level 3 (EV Hub)", i, "Priority", 0, None))

        cursor.executemany("INSERT INTO slots VALUES (?, ?, ?, ?, ?, ?)", slots)

        # Insert sample parked vehicles for realistic demo
        now = datetime.now()
        sample_entries = [
            ("PK-2026-001", "KA-01-MJ-4521", "Car", "Alex Turner", "9876543210", "L1-C07", 
             now.replace(hour=max(0, now.hour - 2), minute=15).isoformat()),
            ("PK-2026-002", "DL-04-EV-9988", "EV", "Sarah Chen", "9845123654", "L3-EV01", 
             now.replace(hour=max(0, now.hour - 1), minute=40).isoformat()),
            ("PK-2026-003", "MH-12-AB-3312", "Two-Wheeler", "Rahul Verma", "9765432190", "L1-B01", 
             now.replace(hour=max(0, now.hour - 3), minute=5).isoformat()),
        ]
        for s_id, plate, v_type, name, phone, slot_id, ent_time in sample_entries:
            cursor.execute("""
                INSERT INTO sessions (id, plate_number, vehicle_type, driver_name, driver_phone, slot_id, entry_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
            """, (s_id, plate, v_type, name, phone, slot_id, ent_time))
            cursor.execute("UPDATE slots SET is_occupied = 1, current_vehicle_id = ? WHERE id = ?", (plate, slot_id))

    conn.commit()
    conn.close()


class ParkingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json(self, data, status=200):
        content = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            conn = get_db()
            cursor = conn.cursor()

            if path == "/api/slots":
                cursor.execute("""
                    SELECT s.*, ses.plate_number, ses.entry_time, ses.id as session_id, ses.driver_name
                    FROM slots s
                    LEFT JOIN sessions ses ON s.id = ses.slot_id AND ses.status = 'active'
                    ORDER BY s.floor, s.slot_number
                """)
                rows = [dict(r) for r in cursor.fetchall()]
                conn.close()
                self.send_json(rows)
                return

            elif path == "/api/sessions/active":
                cursor.execute("""
                    SELECT * FROM sessions WHERE status = 'active' ORDER BY entry_time DESC
                """)
                rows = [dict(r) for r in cursor.fetchall()]
                conn.close()
                self.send_json(rows)
                return

            elif path == "/api/history":
                cursor.execute("""
                    SELECT * FROM sessions WHERE status = 'completed' ORDER BY exit_time DESC LIMIT 100
                """)
                rows = [dict(r) for r in cursor.fetchall()]
                conn.close()
                self.send_json(rows)
                return

            elif path == "/api/rates":
                cursor.execute("SELECT * FROM rates")
                rows = [dict(r) for r in cursor.fetchall()]
                conn.close()
                self.send_json(rows)
                return

            elif path == "/api/stats":
                cursor.execute("SELECT COUNT(*) as total_slots, SUM(is_occupied) as occupied_slots FROM slots")
                slot_stats = cursor.fetchone()
                total_slots = slot_stats["total_slots"] or 0
                occupied_slots = slot_stats["occupied_slots"] or 0
                available_slots = total_slots - occupied_slots

                cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total_revenue, COUNT(*) as exits_today FROM sessions WHERE status = 'completed'")
                rev_stats = cursor.fetchone()

                cursor.execute("""
                    SELECT s.type, COUNT(s.id) as total, COALESCE(SUM(s.is_occupied), 0) as occupied 
                    FROM slots s GROUP BY s.type
                """)
                breakdown = [dict(r) for r in cursor.fetchall()]

                conn.close()
                self.send_json({
                    "total_slots": total_slots,
                    "occupied_slots": occupied_slots,
                    "available_slots": available_slots,
                    "occupancy_rate": round((occupied_slots / total_slots * 100) if total_slots else 0, 1),
                    "total_revenue": round(rev_stats["total_revenue"], 2),
                    "completed_trips": rev_stats["exits_today"],
                    "breakdown": breakdown
                })
                return

            elif path == "/api/network-info":
                local_ip = get_local_ip()
                conn.close()
                self.send_json({
                    "local_ip": local_ip,
                    "port": PORT,
                    "local_url": f"http://localhost:{PORT}",
                    "gadget_url": f"http://{local_ip}:{PORT}"
                })
                return

            conn.close()
            self.send_json({"error": "Not Found"}, 404)
            return

        # Serve static assets
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
            try:
                data = json.loads(body) if body else {}
            except Exception:
                data = {}

            conn = get_db()
            cursor = conn.cursor()

            if path == "/api/checkin":
                plate = data.get("plate_number", "").strip().upper()
                v_type = data.get("vehicle_type", "Car")
                driver_name = data.get("driver_name", "").strip() or "Guest"
                driver_phone = data.get("driver_phone", "").strip() or "-"
                preferred_slot = data.get("slot_id")

                if not plate:
                    conn.close()
                    self.send_json({"error": "Vehicle plate number is required"}, 400)
                    return

                # Check if already parked
                cursor.execute("SELECT id, slot_id FROM sessions WHERE plate_number = ? AND status = 'active'", (plate,))
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    self.send_json({"error": f"Vehicle {plate} is already parked in slot {existing['slot_id']}!"}, 400)
                    return

                # Allocate slot: user preferred or nearest available for vehicle type
                allocated_slot = None
                if preferred_slot:
                    cursor.execute("SELECT id FROM slots WHERE id = ? AND is_occupied = 0", (preferred_slot,))
                    r = cursor.fetchone()
                    if r:
                        allocated_slot = r["id"]

                if not allocated_slot:
                    cursor.execute("SELECT id FROM slots WHERE is_occupied = 0 AND type = ? ORDER BY floor, slot_number LIMIT 1", (v_type,))
                    r = cursor.fetchone()
                    if r:
                        allocated_slot = r["id"]
                    else:
                        cursor.execute("SELECT id FROM slots WHERE is_occupied = 0 ORDER BY floor, slot_number LIMIT 1")
                        r = cursor.fetchone()
                        if r:
                            allocated_slot = r["id"]

                if not allocated_slot:
                    conn.close()
                    self.send_json({"error": "Parking lot is full! No available slots."}, 400)
                    return

                session_id = f"PK-{datetime.now().strftime('%Y%m%d')}-{os.urandom(3).hex().upper()}"
                entry_time = datetime.now().isoformat()

                cursor.execute("""
                    INSERT INTO sessions (id, plate_number, vehicle_type, driver_name, driver_phone, slot_id, entry_time, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                """, (session_id, plate, v_type, driver_name, driver_phone, allocated_slot, entry_time))

                cursor.execute("UPDATE slots SET is_occupied = 1, current_vehicle_id = ? WHERE id = ?", (plate, allocated_slot))
                conn.commit()
                conn.close()

                self.send_json({
                    "success": True,
                    "session_id": session_id,
                    "plate_number": plate,
                    "vehicle_type": v_type,
                    "slot_id": allocated_slot,
                    "driver_name": driver_name,
                    "driver_phone": driver_phone,
                    "entry_time": entry_time
                })
                return

            elif path == "/api/checkout":
                query = data.get("query", "").strip()
                payment_method = data.get("payment_method", "Cash")

                if not query:
                    conn.close()
                    self.send_json({"error": "Vehicle plate or session ID required"}, 400)
                    return

                cursor.execute("""
                    SELECT * FROM sessions 
                    WHERE (plate_number = ? OR id = ? OR slot_id = ?) AND status = 'active'
                """, (query.upper(), query, query))
                session = cursor.fetchone()

                if not session:
                    conn.close()
                    self.send_json({"error": f"No active parking session found for '{query}'"}, 404)
                    return

                session = dict(session)
                entry_dt = datetime.fromisoformat(session["entry_time"])
                exit_dt = datetime.now()
                diff_seconds = (exit_dt - entry_dt).total_seconds()
                duration_minutes = max(1, int(diff_seconds / 60))
                hours_billed = math.ceil(duration_minutes / 60)

                # Get rates
                cursor.execute("SELECT * FROM rates WHERE vehicle_type = ?", (session["vehicle_type"],))
                rate_row = cursor.fetchone()
                if rate_row:
                    base_rate = rate_row["base_rate"]
                    hourly_rate = rate_row["hourly_rate"]
                    daily_max = rate_row["daily_max"]
                    ev_surcharge = rate_row["ev_surcharge"]
                else:
                    base_rate, hourly_rate, daily_max, ev_surcharge = 2.5, 3.0, 25.0, 0.0

                if hours_billed <= 1:
                    total_amount = base_rate
                else:
                    total_amount = base_rate + (hours_billed - 1) * hourly_rate

                if session["vehicle_type"] == "EV":
                    total_amount += ev_surcharge

                days = math.ceil(hours_billed / 24)
                max_allowed = days * daily_max
                if total_amount > max_allowed:
                    total_amount = max_allowed

                total_amount = round(total_amount, 2)
                exit_time_str = exit_dt.isoformat()

                cursor.execute("""
                    UPDATE sessions 
                    SET exit_time = ?, duration_minutes = ?, total_amount = ?, payment_method = ?, status = 'completed'
                    WHERE id = ?
                """, (exit_time_str, duration_minutes, total_amount, payment_method, session["id"]))

                cursor.execute("UPDATE slots SET is_occupied = 0, current_vehicle_id = NULL WHERE id = ?", (session["slot_id"],))

                conn.commit()
                conn.close()

                self.send_json({
                    "success": True,
                    "session_id": session["id"],
                    "plate_number": session["plate_number"],
                    "vehicle_type": session["vehicle_type"],
                    "driver_name": session["driver_name"],
                    "slot_id": session["slot_id"],
                    "entry_time": session["entry_time"],
                    "exit_time": exit_time_str,
                    "duration_minutes": duration_minutes,
                    "hours_billed": hours_billed,
                    "base_rate": base_rate,
                    "hourly_rate": hourly_rate,
                    "ev_surcharge": ev_surcharge if session["vehicle_type"] == "EV" else 0,
                    "total_amount": total_amount,
                    "payment_method": payment_method
                })
                return

            elif path == "/api/reset":
                cursor.execute("DELETE FROM sessions")
                cursor.execute("DELETE FROM slots")
                cursor.execute("DELETE FROM rates")
                conn.commit()
                conn.close()
                init_db()
                self.send_json({"success": True, "message": "Database reset with fresh sample data."})
                return

            conn.close()
            self.send_json({"error": "Endpoint not found"}, 404)
            return

        super().do_POST()


def run():
    init_db()
    local_ip = get_local_ip()
    server_address = ("", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, ParkingHandler)
    print("==================================================================")
    print("  ParkFlow Parking Management System Server is LIVE!")
    print("  ----------------------------------------------------------------")
    print(f"  Local PC:          http://localhost:{PORT}")
    print(f"  Any Phone/Gadget:  http://{local_ip}:{PORT}")
    print("  (Ensure your gadget is connected to the same Wi-Fi network)")
    print("==================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run()
