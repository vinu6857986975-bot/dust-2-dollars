"""
Unit Tests for Deterministic Calculations & Civil Standards (IS 456)
"""
import unittest
from calculations.engine import (
    calculate_concrete_volume,
    calculate_cement_sand_aggregate,
    calculate_steel_requirement,
    calculate_brickwork,
    calculate_finishing
)

class TestDeterministicCalculations(unittest.TestCase):
    def test_concrete_volume(self):
        # 1500 sq.ft residential house with 1 floor
        res = calculate_concrete_volume(1500, floors=1, building_type="residential")
        # 1500 sq.ft = ~139.35 m2 * 0.22 = ~30.66 m3
        self.assertGreater(res["concrete_volume_m3"], 25.0)
        self.assertLess(res["concrete_volume_m3"], 35.0)

    def test_cement_sand_aggregate(self):
        res = calculate_cement_sand_aggregate(30.0, "M20")
        self.assertGreater(res["cement_bags"], 200)
        self.assertGreater(res["sand_m3"], 10.0)
        self.assertGreater(res["aggregate_m3"], 20.0)

    def test_steel_tonnage(self):
        res = calculate_steel_requirement(30.0, "residential")
        # 30 m3 * 82 kg/m3 = 2460 kg = 2.46 tonnes
        self.assertAlmostEqual(res["steel_tonnes"], 2.46, places=1)

    def test_brickwork(self):
        res = calculate_brickwork(1500, floors=1)
        self.assertGreater(res["total_bricks"], 10000)

if __name__ == "__main__":
    unittest.main()
