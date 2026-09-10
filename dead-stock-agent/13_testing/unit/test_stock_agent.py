import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.stock_agent import StockAgent

class TestStockAgent(unittest.TestCase):
    def setUp(self):
        self.agent = StockAgent()

    def test_stock_aging_calculation(self):
        inv = {"quantity": 40, "stock_since": "2025-01-01", "monthly_sales": 2}
        prod = {"cost_price": 1000, "selling_price": 2000, "mrp": 2500}
        supp = {"return_allowed": 1, "return_window_days": 30, "name": "Test Supp"}
        res = self.agent.analyze(inv, prod, supp, [])
        self.assertEqual(res["status"], "ok")
        self.assertGreater(res["metrics"]["age_days"], 100)
        self.assertIn("total_cost_value", res["value"])

if __name__ == '__main__':
    unittest.main()
