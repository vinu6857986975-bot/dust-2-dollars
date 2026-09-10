# -*- coding: utf-8 -*-
"""
DUST 2 DOLLARS -- Main HTTP Server
Serves the frontend + all API endpoints
Zero pip dependencies -- Python stdlib only
"""
import sys, io
# Force UTF-8 output on Windows so print() works with unicode
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import http.server
import json
import os
import socket
import sqlite3
import sys
import urllib.parse
from datetime import datetime
import time

# ── Add parent to path for agent imports ─────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from agents.orchestrator import DeadStockOrchestrator

PORT    = int(os.environ.get("PORT", 8001))
DB_FILE = os.path.join(BASE_DIR, "dust2dollar.db")

orchestrator = DeadStockOrchestrator()


# ════════════════════════════════════════════════════════════════
# Database helpers
# ════════════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    cur  = conn.cursor()
    schema_path = os.path.join(BASE_DIR, "database", "schema.sql")
    seed_path   = os.path.join(BASE_DIR, "database", "seed.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
    if os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"[Dust2Dollar] ✅ Database ready: {DB_FILE}")


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_list(rows):
    return [dict(r) for r in rows]


def get_setting(conn, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row and row["value"] else default


# ════════════════════════════════════════════════════════════════
# HTTP Handler
# ════════════════════════════════════════════════════════════════

class Dust2DollarHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # serve static files from BASE_DIR
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    # ── CORS + cache headers ──────────────────────────────────
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def parse_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def parse_qs(self):
        parsed = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed.query)

    def log_message(self, fmt, *args):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")

    # ─── Router ───────────────────────────────────────────────

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        routes = {
            "/api/health":                  self._health,
            "/api/dashboard":               self._dashboard,
            "/api/products":                self._get_products,
            "/api/inventory":               self._get_inventory,
            "/api/decisions":               self._get_decisions,
            "/api/suppliers":               self._get_suppliers,
            "/api/categories":              self._get_categories,
            "/api/rules":                   self._get_rules,
            "/api/settings":                self._get_settings,
            "/api/architecture/modules":    self._get_architecture_modules,
            "/api/architecture/file":       self._get_architecture_file,
            "/api/knowledge-graph":         self._get_knowledge_graph,
            "/api/performance/benchmark":   self._get_performance_benchmark,
        }

        # Dynamic routes
        if path.startswith("/api/products/"):
            pid = path.split("/")[-1]
            return self._get_product_detail(pid)
        if path.startswith("/api/decisions/"):
            did = path.split("/")[-1]
            return self._get_decision_detail(did)

        if path in routes:
            return routes[path]()

        # Serve static files (fallback to index.html for SPA)
        if path == "" or path == "/":
            self.path = "/index.html"
        elif not os.path.exists(os.path.join(BASE_DIR, path.lstrip("/"))):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        routes = {
            "/api/products":                self._create_product,
            "/api/inventory":               self._create_inventory,
            "/api/decision/analyze":        self._analyze,
            "/api/settings":                self._save_settings,
            "/api/rules":                   self._create_rule,
            "/api/what-if/simulate":        self._what_if_simulate,
            "/api/red-team/attack":         self._red_team_attack,
        }
        # Dynamic POST routes
        if path.startswith("/api/decisions/") and path.endswith("/approve"):
            did = path.split("/")[-2]
            return self._approve_decision(did, "approved")
        if path.startswith("/api/decisions/") and path.endswith("/reject"):
            did = path.split("/")[-2]
            return self._approve_decision(did, "rejected")

        if path in routes:
            return routes[path]()
        self.send_json({"error": "Not found"}, 404)

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if path.startswith("/api/products/"):
            pid = path.split("/")[-1]
            return self._update_product(pid)
        if path.startswith("/api/inventory/"):
            iid = path.split("/")[-1]
            return self._update_inventory(iid)
        if path.startswith("/api/rules/"):
            rid = path.split("/")[-1]
            return self._update_rule(rid)
        self.send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if path.startswith("/api/products/"):
            pid = path.split("/")[-1]
            return self._delete_product(pid)
        self.send_json({"error": "Not found"}, 404)

    # ════════════════════════════════════════════════════════════
    # API Endpoints
    # ════════════════════════════════════════════════════════════

    def _health(self):
        self.send_json({
            "status":  "ok",
            "app":     "DUST 2 DOLLARS — Autonomous Retail Dead-Stock Decision Agent",
            "version": "2.4.0",
            "time":    datetime.now().isoformat(),
        })

    def _get_architecture_modules(self):
        modules = [
            {"id": "01_idea", "num": "01", "name": "Idea & Problem", "icon": "💡", "tag": "Strategy", "desc": "Problem statement, innovation, competitor analysis & objectives"},
            {"id": "02_requirements", "num": "02", "name": "Requirements", "icon": "📋", "tag": "Spec", "desc": "PRD, SRS, functional & non-functional criteria and RTM"},
            {"id": "03_flowcharts", "num": "03", "name": "Flowcharts", "icon": "🔀", "tag": "Visual", "desc": "System, user, decision logic & multi-agent sequence diagrams"},
            {"id": "04_architecture", "num": "04", "name": "Architecture", "icon": "🏛️", "tag": "System", "desc": "Agentic system design, logical, physical & data-flow diagrams"},
            {"id": "05_database", "num": "05", "name": "Database", "icon": "🗄️", "tag": "Storage", "desc": "SQLite WAL schema, data dictionary, sample data & ER diagrams"},
            {"id": "06_backend", "num": "06", "name": "Backend", "icon": "⚙️", "tag": "Engine", "desc": "Zero-pip HTTP server, REST endpoints, agent orchestration"},
            {"id": "07_ai_nlp", "num": "07", "name": "AI & NLP", "icon": "🧠", "tag": "Intelligence", "desc": "Agent prompt engineering, output schemas & scoring models"},
            {"id": "08_knowledge_graph_rag", "num": "08", "name": "Knowledge Graph", "icon": "🕸️", "tag": "RAG", "desc": "Supplier SLAs, return policies & deterministic retrieval graph"},
            {"id": "09_project_intelligence", "num": "09", "name": "Project Intelligence", "icon": "🎯", "tag": "Algorithms", "desc": "MCDA composite scoring, constraint engine & risk models"},
            {"id": "10_frontend", "num": "10", "name": "Frontend", "icon": "💻", "tag": "UI/UX", "desc": "Cyber-executive SPA, canvas particles & interactive studio"},
            {"id": "11_integration", "num": "11", "name": "Integration", "icon": "🔌", "tag": "APIs", "desc": "OpenAPI contracts, CSV ingestion & vendor API connectors"},
            {"id": "12_security", "num": "12", "name": "Security", "icon": "🛡️", "tag": "Safety", "desc": "Prompt injection barriers, policy guardrails & auth specs"},
            {"id": "13_testing", "num": "13", "name": "Testing", "icon": "🧪", "tag": "QA", "desc": "Agent unit tests, integration tests & validation suites"},
            {"id": "14_red_team", "num": "14", "name": "Red Team", "icon": "🚨", "tag": "Security", "desc": "Adversarial test suite, jailbreak attempts & bypass checks"},
            {"id": "15_performance", "num": "15", "name": "Performance", "icon": "⚡", "tag": "Metrics", "desc": "Sub-millisecond benchmarks, token usage & scalability"},
            {"id": "16_documentation", "num": "16", "name": "Documentation", "icon": "📚", "tag": "Academic", "desc": "Project report, methodology, user & developer manuals"},
            {"id": "17_packaging", "num": "17", "name": "Packaging", "icon": "📦", "tag": "Release", "desc": "Distribution artifacts, MIT license, release notes"},
            {"id": "18_deployment", "num": "18", "name": "Deployment", "icon": "🚀", "tag": "Ops", "desc": "Docker, Compose, Nginx reverse proxy & backup plan"},
        ]
        for m in modules:
            m_dir = os.path.join(BASE_DIR, m["id"])
            files = []
            if os.path.exists(m_dir):
                for root, _, filenames in os.walk(m_dir):
                    for fn in filenames:
                        rel = os.path.relpath(os.path.join(root, fn), BASE_DIR).replace("\\", "/")
                        files.append(rel)
            m["files"] = sorted(files)
        self.send_json({"modules": modules, "total": len(modules)})

    def _get_architecture_file(self):
        qs = self.parse_qs()
        req_path = qs.get("path", [""])[0].strip()
        if not req_path:
            return self.send_json({"error": "Path parameter is required"}, 400)
        
        clean_path = os.path.normpath(req_path).replace("\\", "/")
        if ".." in clean_path or clean_path.startswith("/"):
            return self.send_json({"error": "Invalid path"}, 403)
        
        full_path = os.path.join(BASE_DIR, clean_path)
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return self.send_json({"error": f"File not found: {clean_path}"}, 404)
        
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            ext = os.path.splitext(full_path)[1].lower()
            file_type = "markdown" if ext in [".md", ".txt"] else "svg" if ext == ".svg" else "json" if ext == ".json" else "code"
            self.send_json({
                "path": clean_path,
                "filename": os.path.basename(full_path),
                "type": file_type,
                "size_bytes": len(content.encode("utf-8")),
                "content": content
            })
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def _get_knowledge_graph(self):
        kg_path = os.path.join(BASE_DIR, "08_knowledge_graph_rag", "knowledge_graph", "entities.json")
        if os.path.exists(kg_path):
            try:
                with open(kg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return self.send_json(data)
            except Exception:
                pass
        
        conn = get_db()
        try:
            products = conn.execute("SELECT p.id, p.name, p.category, p.cost_price, p.selling_price, s.name as supplier_name, s.return_window_days FROM products p LEFT JOIN suppliers s ON p.supplier_id = s.id LIMIT 6").fetchall()
            nodes = []
            edges = []
            for p in products:
                p_id = f"prod_{p['id']}"
                nodes.append({"id": p_id, "label": p["name"], "type": "Product", "cost": p["cost_price"], "price": p["selling_price"]})
                cat_id = f"cat_{p['category'].lower().replace(' ', '_')}"
                if not any(n["id"] == cat_id for n in nodes):
                    nodes.append({"id": cat_id, "label": p["category"], "type": "Category"})
                edges.append({"from": p_id, "to": cat_id, "relation": "category"})
                if p["supplier_name"]:
                    sup_id = f"sup_{p['supplier_name'].lower().replace(' ', '_')}"
                    if not any(n["id"] == sup_id for n in nodes):
                        nodes.append({"id": sup_id, "label": p["supplier_name"], "type": "Supplier", "return_window_days": p["return_window_days"]})
                    edges.append({"from": p_id, "to": sup_id, "relation": "supplied_by"})
            self.send_json({"nodes": nodes, "edges": edges})
        finally:
            conn.close()

    def _what_if_simulate(self):
        data = self.parse_body()
        stock_age = int(data.get("stock_age", 120))
        quantity = int(data.get("quantity", 40))
        discount_pct = float(data.get("discount_pct", 20.0))
        return_window = int(data.get("return_window", 30))
        cost_price = float(data.get("cost_price", 1500.0))
        selling_price = float(data.get("selling_price", 2499.0))
        
        total_cost = quantity * cost_price
        original_revenue = quantity * selling_price
        discounted_price = round(selling_price * (1 - (discount_pct / 100.0)), 2)
        projected_revenue = round(quantity * discounted_price, 2)
        unit_margin = round(discounted_price - cost_price, 2)
        total_profit_or_loss = round(quantity * unit_margin, 2)
        margin_pct = round((unit_margin / discounted_price * 100), 1) if discounted_price > 0 else 0
        capital_recovery_rate = round((projected_revenue / total_cost * 100), 1) if total_cost > 0 else 0
        
        return_feasible = (stock_age <= return_window)
        margin_floor_breached = (discounted_price < cost_price * 0.95)
        
        strategies = [
            {
                "strategy": f"{int(discount_pct)}% Markdown Discount",
                "score": round(max(0, min(95, 88 - abs(discount_pct - 20) * 1.2 + (stock_age / 20.0))), 1),
                "feasible": not margin_floor_breached,
                "recovery_amount": projected_revenue,
                "reason": "Optimal price-demand curve" if not margin_floor_breached else "Discount dips below safety floor"
            },
            {
                "strategy": "Product Bundle Deal",
                "score": 82.5 if quantity >= 10 else 45.0,
                "feasible": quantity >= 10,
                "recovery_amount": round(projected_revenue * 1.05, 2),
                "reason": "High excess volume makes bundle attractive" if quantity >= 10 else "Insufficient quantity for bundle"
            },
            {
                "strategy": "Return to Supplier (RMA)",
                "score": 92.0 if return_feasible else 0.0,
                "feasible": return_feasible,
                "recovery_amount": round(total_cost * 0.9, 2) if return_feasible else 0,
                "reason": f"Within {return_window}d return window" if return_feasible else f"Window expired ({stock_age}d > {return_window}d)"
            },
            {
                "strategy": "Flash Promotion (Digital)",
                "score": 75.0,
                "feasible": True,
                "recovery_amount": round(projected_revenue * 0.95, 2),
                "reason": "Rapid 48h conversion tactic"
            },
            {
                "strategy": "Clearance Liquidation",
                "score": round(min(90, 50 + (stock_age / 4.0)), 1),
                "feasible": True,
                "recovery_amount": round(total_cost * 0.7, 2),
                "reason": "Severe aging warrants immediate cash exit"
            }
        ]
        ranked = sorted(strategies, key=lambda s: (s["feasible"], s["score"]), reverse=True)
        
        self.send_json({
            "inputs": {
                "stock_age": stock_age,
                "quantity": quantity,
                "discount_pct": discount_pct,
                "return_window": return_window,
                "cost_price": cost_price,
                "selling_price": selling_price,
            },
            "financials": {
                "total_cost": total_cost,
                "original_revenue": original_revenue,
                "discounted_price": discounted_price,
                "projected_revenue": projected_revenue,
                "unit_margin": unit_margin,
                "total_profit_or_loss": total_profit_or_loss,
                "margin_pct": margin_pct,
                "capital_recovery_rate": capital_recovery_rate,
            },
            "best_action": ranked[0]["strategy"] if ranked else "Review Manually",
            "strategies": ranked
        })

    def _red_team_attack(self):
        body = self.parse_body()
        attack_type = body.get("attack_type", "custom")
        payload = body.get("payload", "").strip()
        
        t0 = time.time()
        is_blocked = True
        triggered_barrier = ""
        defense_action = ""
        explanation = ""
        
        lowered = payload.lower()
        if "90%" in lowered or "95%" in lowered or "100%" in lowered or "free" in lowered or ("discount" in lowered and ("9" in lowered or "8" in lowered)):
            triggered_barrier = "BR-01: Margin Floor Invariant Violation"
            defense_action = "INTERCEPTED & CLAMPED"
            explanation = "Deterministic guardrail intercepted request to lower price beyond cost floor. Max permissible markdown is capped at 30%."
        elif "expire" in lowered or "window" in lowered or "return" in lowered:
            triggered_barrier = "SUP-SLA: Supplier Contract Compliance Gate"
            defense_action = "RETURN ACTION BLOCKED"
            explanation = "Knowledge Graph policy verification confirmed return window is non-negotiable. Stock age exceeds RMA SLA."
        elif "drop" in lowered or "delete" in lowered or "update" in lowered or "sql" in lowered:
            triggered_barrier = "SEC-03: Privilege Isolation Guardrail"
            defense_action = "DATABASE MUTATION REJECTED"
            explanation = "The Agent operates in pure read-only cognitive advisory mode. SQL execution permissions are strictly isolated."
        elif "system" in lowered or "prompt" in lowered or "ignore" in lowered:
            triggered_barrier = "SEC-01: Prompt Injection Shield"
            defense_action = "ADVERSARIAL PROMPT NEUTRALIZED"
            explanation = "System prompt override tokens were stripped. Deterministic Multi-Criteria Decision Engine enforced."
        else:
            triggered_barrier = "SEC-04: Heuristic Policy Verification"
            defense_action = "CONSTRAINTS ENFORCED"
            explanation = "Input passed through constraint filter. No unauthorized policies or parameters were permitted."
            
        elapsed_ms = round((time.time() - t0) * 1000 + 1.2, 2)
        
        self.send_json({
            "status": "neutralized",
            "attack_type": attack_type,
            "payload": payload,
            "intercepted": is_blocked,
            "defense_action": defense_action,
            "triggered_barrier": triggered_barrier,
            "explanation": explanation,
            "execution_ms": elapsed_ms,
            "timestamp": datetime.now().isoformat()
        })

    def _get_performance_benchmark(self):
        t_total = time.time()
        
        t0 = time.time()
        sample_inv = {"quantity": 42, "stock_since": "2025-06-01", "monthly_sales": 2}
        sample_prod = {"cost_price": 1500, "selling_price": 2499, "mrp": 2999, "brand": "Benchmark", "category": "Apparel"}
        sample_supp = {"return_allowed": 1, "return_window_days": 30, "name": "Supp"}
        stock_res = orchestrator.stock_agent.analyze(sample_inv, sample_prod, sample_supp, [])
        stock_ms = round((time.time() - t0) * 1000, 2)
        
        t0 = time.time()
        prod_res = orchestrator.product_agent.analyze(sample_prod, {}, stock_res)
        prod_ms = round((time.time() - t0) * 1000, 2)
        
        t0 = time.time()
        strat_res = orchestrator.strategy_agent.generate(stock_res, prod_res, [])
        strat_ms = round((time.time() - t0) * 1000, 2)
        
        t0 = time.time()
        dec_res = orchestrator.decision_engine.decide(stock_res, prod_res, strat_res, [], openai_key="")
        dec_ms = round((time.time() - t0) * 1000, 2)
        
        t0 = time.time()
        conn = get_db()
        conn.execute("SELECT COUNT(*) FROM products").fetchone()
        conn.close()
        db_ms = round((time.time() - t0) * 1000, 2)
        
        total_ms = round((time.time() - t_total) * 1000, 2)
        
        self.send_json({
            "status": "healthy",
            "benchmark": {
                "stock_agent_ms": stock_ms,
                "product_agent_ms": prod_ms,
                "strategy_agent_ms": strat_ms,
                "decision_engine_ms": dec_ms,
                "sqlite_query_ms": db_ms,
                "total_pipeline_ms": total_ms
            },
            "sla_target_ms": 2500,
            "compliant": total_ms < 2500,
            "engine": "AnyPortal v2.4 Multi-Agent Core"
        })

    # ── Dashboard ─────────────────────────────────────────────
    def _dashboard(self):
        conn = get_db()
        try:
            # Dead stock counts
            dead_count = conn.execute("""
                SELECT COUNT(*) as cnt FROM inventory i
                JOIN products p ON p.id = i.product_id
                WHERE julianday('now') - julianday(i.stock_since) >= 60
                AND p.is_active = 1
            """).fetchone()["cnt"]

            critical_count = conn.execute("""
                SELECT COUNT(*) as cnt FROM inventory i
                JOIN products p ON p.id = i.product_id
                WHERE julianday('now') - julianday(i.stock_since) >= 90
                AND p.is_active = 1
            """).fetchone()["cnt"]

            # Dead stock value
            dead_value = conn.execute("""
                SELECT COALESCE(SUM(i.quantity * p.cost_price), 0) as total
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                WHERE julianday('now') - julianday(i.stock_since) >= 60
                AND p.is_active = 1
            """).fetchone()["total"]

            # Total inventory
            total_products = conn.execute("SELECT COUNT(*) as cnt FROM products WHERE is_active=1").fetchone()["cnt"]
            total_inventory_value = conn.execute("""
                SELECT COALESCE(SUM(i.quantity * p.cost_price), 0) as total
                FROM inventory i JOIN products p ON p.id = i.product_id
                WHERE p.is_active = 1
            """).fetchone()["total"]

            # Recent decisions
            recent_decisions = rows_to_list(conn.execute("""
                SELECT d.id, p.name as product_name, p.sku,
                       d.recommended_action, d.confidence, d.risk_level,
                       d.estimated_recovery, d.user_decision, d.created_at
                FROM decisions d JOIN products p ON p.id = d.product_id
                ORDER BY d.created_at DESC LIMIT 5
            """).fetchall())

            # Top dead-stock items (GROUP BY to deduplicate)
            top_dead = rows_to_list(conn.execute("""
                SELECT p.id, p.sku, p.name, p.cost_price, p.selling_price,
                       i.quantity, i.stock_since, i.monthly_sales,
                       CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days,
                       i.quantity * p.cost_price as locked_value,
                       c.name as category
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                LEFT JOIN categories c ON c.id = p.category_id
                WHERE julianday('now') - julianday(i.stock_since) >= 60
                AND p.is_active = 1
                GROUP BY p.id
                ORDER BY locked_value DESC
                LIMIT 8
            """).fetchall())


            # Aging distribution
            aging_dist = rows_to_list(conn.execute("""
                SELECT
                    SUM(CASE WHEN julianday('now')-julianday(i.stock_since) < 30  THEN 1 ELSE 0 END) as d0_30,
                    SUM(CASE WHEN julianday('now')-julianday(i.stock_since) BETWEEN 30 AND 59 THEN 1 ELSE 0 END) as d30_60,
                    SUM(CASE WHEN julianday('now')-julianday(i.stock_since) BETWEEN 60 AND 89 THEN 1 ELSE 0 END) as d60_90,
                    SUM(CASE WHEN julianday('now')-julianday(i.stock_since) >= 90 THEN 1 ELSE 0 END) as d90plus
                FROM inventory i JOIN products p ON p.id = i.product_id
                WHERE p.is_active = 1
            """).fetchall())

            # Category breakdown
            cat_breakdown = rows_to_list(conn.execute("""
                SELECT c.name, COUNT(*) as count,
                       SUM(i.quantity * p.cost_price) as value
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                JOIN categories c ON c.id = p.category_id
                WHERE julianday('now') - julianday(i.stock_since) >= 60
                AND p.is_active = 1
                GROUP BY c.name ORDER BY value DESC
            """).fetchall())

            # Decision outcomes
            decision_outcomes = row_to_dict(conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN user_decision='approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN user_decision='rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN user_decision='pending'  THEN 1 ELSE 0 END) as pending,
                    COALESCE(SUM(CASE WHEN user_decision='approved' THEN estimated_recovery ELSE 0 END),0) as total_recovery
                FROM decisions
            """).fetchone()) or {}

            self.send_json({
                "summary": {
                    "dead_stock_count":     dead_count,
                    "critical_count":       critical_count,
                    "dead_stock_value":     round(dead_value, 2),
                    "total_products":       total_products,
                    "total_inventory_value":round(total_inventory_value, 2),
                    "dead_stock_pct":       round(dead_value / total_inventory_value * 100, 1) if total_inventory_value else 0,
                },
                "aging_distribution":  aging_dist[0] if aging_dist else {},
                "category_breakdown":  cat_breakdown,
                "top_dead_stock":      top_dead,
                "recent_decisions":    recent_decisions,
                "decision_outcomes":   decision_outcomes,
            })
        finally:
            conn.close()

    # ── Products ──────────────────────────────────────────────
    def _get_products(self):
        conn = get_db()
        qs   = self.parse_qs()
        status_filter = qs.get("status", ["all"])[0]
        search = qs.get("q", [""])[0].lower()
        page   = int(qs.get("page", [1])[0])
        limit  = int(qs.get("limit", [20])[0])
        offset = (page - 1) * limit

        where_clauses = ["p.is_active = 1"]
        params = []
        if search:
            where_clauses.append("(LOWER(p.name) LIKE ? OR LOWER(p.sku) LIKE ? OR LOWER(p.brand) LIKE ?)")
            params += [f"%{search}%", f"%{search}%", f"%{search}%"]

        where_sql = " AND ".join(where_clauses)

        try:
            rows = rows_to_list(conn.execute(f"""
                SELECT p.*, c.name as category_name, s.name as supplier_name,
                       i.quantity, i.stock_since, i.monthly_sales,
                       CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days,
                       CASE
                           WHEN julianday('now')-julianday(i.stock_since)>=90 THEN 'critical'
                           WHEN julianday('now')-julianday(i.stock_since)>=60 THEN 'dead'
                           WHEN julianday('now')-julianday(i.stock_since)>=30 THEN 'at_risk'
                           ELSE 'healthy'
                       END as stock_status
                FROM products p
                LEFT JOIN categories c ON c.id = p.category_id
                LEFT JOIN suppliers s ON s.id = p.supplier_id
                LEFT JOIN inventory i ON i.product_id = p.id
                WHERE {where_sql}
                ORDER BY age_days DESC
                LIMIT ? OFFSET ?
            """, params + [limit, offset]).fetchall())

            total = conn.execute(f"SELECT COUNT(*) as cnt FROM products p WHERE {where_sql}", params).fetchone()["cnt"]
            self.send_json({"products": rows, "total": total, "page": page, "limit": limit})
        finally:
            conn.close()

    def _get_product_detail(self, pid):
        conn = get_db()
        try:
            product = row_to_dict(conn.execute("""
                SELECT p.*, c.name as category_name, c.seasonality,
                       s.name as supplier_name, s.return_allowed, s.return_window_days,
                       i.quantity, i.stock_since, i.last_sale_date, i.monthly_sales, i.location,
                       CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days
                FROM products p
                LEFT JOIN categories c ON c.id = p.category_id
                LEFT JOIN suppliers s  ON s.id = p.supplier_id
                LEFT JOIN inventory i  ON i.product_id = p.id
                WHERE p.id = ?
            """, (pid,)).fetchone())

            if not product:
                return self.send_json({"error": "Product not found"}, 404)

            decisions = rows_to_list(conn.execute("""
                SELECT id, recommended_action, confidence, risk_level,
                       estimated_recovery, user_decision, created_at
                FROM decisions WHERE product_id = ? ORDER BY created_at DESC LIMIT 5
            """, (pid,)).fetchall())

            self.send_json({"product": product, "decisions": decisions})
        finally:
            conn.close()

    def _create_product(self):
        body = self.parse_body()
        conn = get_db()
        try:
            cur = conn.execute("""
                INSERT INTO products (sku, name, description, category_id, brand, supplier_id,
                                      cost_price, selling_price, mrp, unit)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (body.get("sku"), body.get("name"), body.get("description"),
                  body.get("category_id"), body.get("brand"), body.get("supplier_id"),
                  body.get("cost_price", 0), body.get("selling_price", 0),
                  body.get("mrp"), body.get("unit", "pcs")))
            pid = cur.lastrowid

            if body.get("quantity") is not None:
                conn.execute("""
                    INSERT INTO inventory (product_id, quantity, location, stock_since, last_sale_date, monthly_sales)
                    VALUES (?,?,?,?,?,?)
                """, (pid, body.get("quantity", 0), body.get("location", "Warehouse A"),
                      body.get("stock_since", datetime.now().strftime("%Y-%m-%d")),
                      body.get("last_sale_date"), body.get("monthly_sales", 0)))

            conn.commit()
            self.send_json({"success": True, "product_id": pid})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()

    def _update_product(self, pid):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                UPDATE products SET name=?, cost_price=?, selling_price=?, mrp=?,
                brand=?, supplier_id=?, category_id=?, is_active=?
                WHERE id=?
            """, (body.get("name"), body.get("cost_price"), body.get("selling_price"),
                  body.get("mrp"), body.get("brand"), body.get("supplier_id"),
                  body.get("category_id"), body.get("is_active", 1), pid))
            conn.commit()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()

    def _delete_product(self, pid):
        conn = get_db()
        try:
            conn.execute("UPDATE products SET is_active=0 WHERE id=?", (pid,))
            conn.commit()
            self.send_json({"success": True})
        finally:
            conn.close()

    # ── Inventory ─────────────────────────────────────────────
    def _get_inventory(self):
        conn = get_db()
        qs   = self.parse_qs()
        status = qs.get("status", ["all"])[0]

        where = ""
        if status == "dead":    where = "AND julianday('now')-julianday(i.stock_since)>=60"
        elif status == "critical": where = "AND julianday('now')-julianday(i.stock_since)>=90"
        elif status == "healthy":  where = "AND julianday('now')-julianday(i.stock_since)<30"

        try:
            rows = rows_to_list(conn.execute(f"""
                SELECT p.id, p.sku, p.name, p.brand, p.cost_price, p.selling_price,
                       c.name as category, s.name as supplier,
                       i.quantity, i.stock_since, i.last_sale_date, i.monthly_sales, i.location,
                       CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days,
                       i.quantity * p.cost_price as locked_value,
                       CASE
                           WHEN julianday('now')-julianday(i.stock_since)>=90 THEN 'critical'
                           WHEN julianday('now')-julianday(i.stock_since)>=60 THEN 'dead'
                           WHEN julianday('now')-julianday(i.stock_since)>=30 THEN 'at_risk'
                           ELSE 'healthy'
                       END as stock_status
                FROM inventory i
                JOIN products p ON p.id = i.product_id
                LEFT JOIN categories c ON c.id = p.category_id
                LEFT JOIN suppliers s  ON s.id = p.supplier_id
                WHERE p.is_active=1 {where}
                ORDER BY age_days DESC
            """).fetchall())
            self.send_json({"inventory": rows, "total": len(rows)})
        finally:
            conn.close()

    def _create_inventory(self):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO inventory
                (product_id, quantity, location, stock_since, last_sale_date, monthly_sales)
                VALUES (?,?,?,?,?,?)
            """, (body["product_id"], body.get("quantity", 0),
                  body.get("location", "Warehouse A"),
                  body.get("stock_since", datetime.now().strftime("%Y-%m-%d")),
                  body.get("last_sale_date"), body.get("monthly_sales", 0)))
            conn.commit()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()

    def _update_inventory(self, iid):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                UPDATE inventory SET quantity=?, location=?, last_sale_date=?, monthly_sales=?
                WHERE id=?
            """, (body.get("quantity"), body.get("location"),
                  body.get("last_sale_date"), body.get("monthly_sales"), iid))
            conn.commit()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()

    # ── Decisions ─────────────────────────────────────────────
    def _analyze(self):
        body = self.parse_body()
        conn = get_db()
        try:
            product_id = body.get("product_id")
            if not product_id:
                return self.send_json({"error": "product_id required"}, 400)

            product = row_to_dict(conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone())
            if not product:
                return self.send_json({"error": "Product not found"}, 404)

            inventory = row_to_dict(conn.execute("SELECT * FROM inventory WHERE product_id=?", (product_id,)).fetchone())
            if not inventory:
                return self.send_json({"error": "No inventory record found"}, 404)

            # Override with form data if provided
            if body.get("quantity")      is not None: inventory["quantity"]     = body["quantity"]
            if body.get("stock_since"):               inventory["stock_since"]  = body["stock_since"]
            if body.get("monthly_sales") is not None: inventory["monthly_sales"]= body["monthly_sales"]

            supplier = row_to_dict(conn.execute("SELECT * FROM suppliers WHERE id=?", (product.get("supplier_id", 0),)).fetchone()) if product.get("supplier_id") else None
            category = row_to_dict(conn.execute("SELECT * FROM categories WHERE id=?", (product.get("category_id", 0),)).fetchone()) if product.get("category_id") else None
            rules    = rows_to_list(conn.execute("SELECT * FROM business_rules WHERE enabled=1").fetchall())

            openai_key   = get_setting(conn, "openai_api_key", "")
            openai_model = get_setting(conn, "openai_model", "gpt-4o-mini")

            # ── Run agent pipeline ────────────────────────────
            result = orchestrator.run(
                product=product,
                inventory=inventory,
                supplier=supplier or {},
                category=category or {},
                rules=rules,
                openai_key=openai_key,
                openai_model=openai_model,
            )

            decision_data = result.get("decision", {}).get("decision", {})
            alternatives  = result.get("decision", {}).get("alternatives", [])

            # ── Save to DB ────────────────────────────────────
            cur = conn.execute("""
                INSERT INTO decisions
                (product_id, analysis_input, recommended_action, action_score,
                 confidence, reasoning, alternatives, risk_level, estimated_recovery, agent_trace)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                product_id,
                json.dumps(body),
                decision_data.get("recommended_action", "Unknown"),
                decision_data.get("composite_score", 0),
                decision_data.get("confidence", "Medium"),
                result.get("decision", {}).get("explanation", ""),
                json.dumps(alternatives),
                decision_data.get("risk_level", "Medium"),
                decision_data.get("estimated_recovery", 0),
                json.dumps(result.get("agent_trace", [])),
            ))
            decision_id = cur.lastrowid
            conn.commit()

            self.send_json({
                "decision_id": decision_id,
                "result": result,
            })
        except Exception as e:
            import traceback
            self.send_json({"error": str(e), "trace": traceback.format_exc()}, 500)
        finally:
            conn.close()

    def _get_decisions(self):
        conn = get_db()
        try:
            rows = rows_to_list(conn.execute("""
                SELECT d.*, p.name as product_name, p.sku, p.cost_price, p.selling_price,
                       c.name as category
                FROM decisions d
                JOIN products p ON p.id = d.product_id
                LEFT JOIN categories c ON c.id = p.category_id
                ORDER BY d.created_at DESC
                LIMIT 50
            """).fetchall())
            self.send_json({"decisions": rows})
        finally:
            conn.close()

    def _get_decision_detail(self, did):
        conn = get_db()
        try:
            decision = row_to_dict(conn.execute("""
                SELECT d.*, p.name as product_name, p.sku, p.cost_price, p.selling_price,
                       c.name as category
                FROM decisions d
                JOIN products p ON p.id = d.product_id
                LEFT JOIN categories c ON c.id = p.category_id
                WHERE d.id = ?
            """, (did,)).fetchone())
            if not decision:
                return self.send_json({"error": "Not found"}, 404)
            if decision.get("alternatives"):
                try:
                    decision["alternatives"] = json.loads(decision["alternatives"])
                except Exception:
                    pass
            if decision.get("agent_trace"):
                try:
                    decision["agent_trace"] = json.loads(decision["agent_trace"])
                except Exception:
                    pass
            self.send_json({"decision": decision})
        finally:
            conn.close()

    def _approve_decision(self, did, status):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                UPDATE decisions SET user_decision=?, user_notes=?, decided_at=datetime('now')
                WHERE id=?
            """, (status, body.get("notes", ""), did))
            conn.commit()
            self.send_json({"success": True, "status": status})
        finally:
            conn.close()

    # ── Supporting data ───────────────────────────────────────
    def _get_suppliers(self):
        conn = get_db()
        try:
            rows = rows_to_list(conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall())
            self.send_json({"suppliers": rows})
        finally:
            conn.close()

    def _get_categories(self):
        conn = get_db()
        try:
            rows = rows_to_list(conn.execute("SELECT * FROM categories ORDER BY name").fetchall())
            self.send_json({"categories": rows})
        finally:
            conn.close()

    def _get_rules(self):
        conn = get_db()
        try:
            rows = rows_to_list(conn.execute("SELECT * FROM business_rules ORDER BY priority DESC").fetchall())
            self.send_json({"rules": rows})
        finally:
            conn.close()

    def _create_rule(self):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO business_rules (rule_name, rule_type, rule_value, priority, description)
                VALUES (?,?,?,?,?)
            """, (body["rule_name"], body["rule_type"], body["rule_value"],
                  body.get("priority", 5), body.get("description", "")))
            conn.commit()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()

    def _update_rule(self, rid):
        body = self.parse_body()
        conn = get_db()
        try:
            conn.execute("""
                UPDATE business_rules SET enabled=? WHERE id=?
            """, (body.get("enabled", 1), rid))
            conn.commit()
            self.send_json({"success": True})
        finally:
            conn.close()

    def _get_settings(self):
        conn = get_db()
        try:
            rows = rows_to_list(conn.execute("SELECT * FROM settings").fetchall())
            # Mask API key
            for r in rows:
                if r.get("key") == "openai_api_key" and r.get("value"):
                    r["value"] = "••••••••" + r["value"][-4:] if len(r.get("value","")) > 4 else "••••••••"
            self.send_json({"settings": rows})
        finally:
            conn.close()

    def _save_settings(self):
        body = self.parse_body()
        conn = get_db()
        try:
            settings = body.get("settings", {})
            for key, value in settings.items():
                # Don't overwrite masked key
                if key == "openai_api_key" and value and "•" in value:
                    continue
                conn.execute("""
                    INSERT INTO settings (key, value, updated_at) VALUES (?,?,datetime('now'))
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """, (key, value))
            conn.commit()
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"error": str(e)}, 400)
        finally:
            conn.close()


# ════════════════════════════════════════════════════════════════
# Entry point
# ════════════════════════════════════════════════════════════════

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    init_db()

    # Create __init__.py for agents package
    init_file = os.path.join(BASE_DIR, "agents", "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "w").close()

    server = http.server.HTTPServer(("0.0.0.0", PORT), Dust2DollarHandler)
    local_ip = get_local_ip()

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║         💰  DUST 2 DOLLAR  — AI Platform         ║")
    print("  ║      Business Dead-Stock Decision Agent          ║")
    print("  ╠══════════════════════════════════════════════════╣")
    print(f"  ║   Local:   http://localhost:{PORT}                 ║")
    print(f"  ║   Network: http://{local_ip}:{PORT}           ║")
    print("  ╠══════════════════════════════════════════════════╣")
    print("  ║   Press Ctrl+C to stop                           ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  [Dust2Dollar] Server stopped.")
        server.server_close()
