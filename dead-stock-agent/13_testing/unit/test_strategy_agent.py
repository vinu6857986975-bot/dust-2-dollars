import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.stock_agent import StockAgent
from agents.product_agent import ProductAgent
from agents.strategy_agent import StrategyAgent

class TestStrategyAgent(unittest.TestCase):
    def setUp(self):
        self.stock_agent = StockAgent()
        self.product_agent = ProductAgent()
        self.strategy_agent = StrategyAgent()

    def test_candidate_generation(self):
        inv = {"quantity": 42, "stock_since": "2025-01-01", "monthly_sales": 1}
        prod = {"id": 1, "name": "Winter Parka", "category": "Apparel", "cost_price": 1500, "selling_price": 2499, "mrp": 2999, "brand": "Nordic"}
        supp = {"return_allowed": 1, "return_window_days": 30, "name": "Nordic Weavers"}
        
        stock_res = self.stock_agent.analyze(inv, prod, supp, [])
        prod_res = self.product_agent.analyze(prod, {}, stock_res)
        res = self.strategy_agent.generate(stock_res, prod_res, [])
        
        self.assertEqual(res["status"], "ok")
        self.assertIn("actions", res)
        self.assertGreaterEqual(len(res["actions"]), 4)

if __name__ == '__main__':
    unittest.main()
