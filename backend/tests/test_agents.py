"""
Unit Tests for Agent Pipeline & Bounded Replanning
"""
import unittest
from agents.pipeline import ConstructAgentsPipeline

class TestAgentPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ConstructAgentsPipeline()

    def test_full_pipeline_run(self):
        project = {
            "id": 101,
            "project_name": "2BHK Residential House - Hyderabad",
            "building_type": "residential",
            "floor_area": 1500,
            "floors": 1,
            "preset": "apartment"
        }
        res = self.pipeline.run_orchestrator(project)
        self.assertEqual(res["status"], "success")
        self.assertIn("vision", res["outputs"])
        self.assertIn("estimation", res["outputs"])
        self.assertIn("material", res["outputs"])
        self.assertIn("cost", res["outputs"])
        self.assertIn("supplier", res["outputs"])
        self.assertIn("verification", res["outputs"])
        self.assertTrue(res["outputs"]["verification"]["passed"])

    def test_bounded_replan_loop(self):
        project = {
            "id": 102,
            "project_name": "Replan Test",
            "building_type": "residential",
            "floor_area": 1500,
            "floors": 1
        }
        # Force price anomaly to trigger replan
        res = self.pipeline.run_orchestrator(project, simulate_violation={
            "rule_id": "V-04",
            "stage": "cost_agent",
            "reason": "Steel price 3x historical average spike"
        })
        self.assertTrue(res["replan_occurred"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["retries"].get("cost_agent"), 1)

if __name__ == "__main__":
    unittest.main()
