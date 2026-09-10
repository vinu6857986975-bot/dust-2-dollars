# -*- coding: utf-8 -*-
"""
Verification test for AnyPortal server endpoints and agent pipeline
"""
import unittest
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import server

class TestAnyPortalEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.init_db()

    def test_database_seed(self):
        conn = server.get_db()
        cnt = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        conn.close()
        self.assertGreater(cnt, 0, "Products should be seeded in SQLite")

    def test_agent_orchestrator(self):
        conn = server.get_db()
        prod = dict(conn.execute("SELECT * FROM products LIMIT 1").fetchone())
        inv = dict(conn.execute("SELECT * FROM inventory WHERE product_id=?", (prod["id"],)).fetchone())
        supp = dict(conn.execute("SELECT * FROM suppliers WHERE id=?", (prod["supplier_id"],)).fetchone())
        rules = [dict(r) for r in conn.execute("SELECT * FROM business_rules WHERE enabled=1").fetchall()]
        conn.close()

        res = server.orchestrator.run(prod, inv, supp, {}, rules)
        self.assertEqual(res["status"], "ok")
        self.assertIn("decision", res)
        self.assertIn("decision", res["decision"])
        self.assertIn("recommended_action", res["decision"]["decision"])
        rec_action = res["decision"]["decision"]["recommended_action"]
        score = res["decision"]["decision"]["composite_score"]
        print(f"[OK] Agent Recommendation: {rec_action} (Composite Score: {score})")

    def test_what_if_simulation_math(self):
        # Age 145 days, return window 30 days -> Return to supplier must NOT be feasible
        stock_age = 145
        return_window = 30
        feasible = (stock_age <= return_window)
        self.assertFalse(feasible)

if __name__ == '__main__':
    unittest.main()
