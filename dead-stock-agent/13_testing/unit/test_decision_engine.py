# -*- coding: utf-8 -*-
"""
Unit tests for Decision Engine
"""
import unittest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from agents.decision_engine import DecisionEngine

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine()

    def test_supplier_return_blocking(self):
        stock_result = {"age_days": 145, "status": "ok"}
        product_result = {"margin_pct": 35.0, "status": "ok"}
        strategy_result = {
            "candidates": [
                {"action": "RETURN_SUPPLIER", "score": 90, "feasible": False, "reason": "Window expired"},
                {"action": "DISCOUNT", "score": 85, "feasible": True}
            ]
        }
        res = self.engine.decide(stock_result, product_result, strategy_result, [])
        self.assertNotEqual(res.get("recommended_action"), "RETURN_SUPPLIER")

if __name__ == '__main__':
    unittest.main()
