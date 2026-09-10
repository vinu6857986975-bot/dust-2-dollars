"""
Cement, Sand, and Aggregate conversion using documented IS 456 assumptions.
Dry Volume factor = 1.54
M20 Mix Ratio = 1 : 1.5 : 3 (Sum = 5.5)
"""
import math

def calculate_cement_bags(concrete_volume_m3: float, mix_ratio: str = "M20") -> dict:
    ratios = {"M15": (1, 2, 4, 7.0), "M20": (1, 1.5, 3, 5.5), "M25": (1, 1, 2, 4.0)}
    c, s, a, sum_parts = ratios.get(mix_ratio, (1, 1.5, 3, 5.5))
    dry_volume = concrete_volume_m3 * 1.54
    cement_m3 = (c / sum_parts) * dry_volume
    cement_kg = cement_m3 * 1440
    cement_bags = math.ceil(cement_kg / 50)
    return {
        "cement_bags": cement_bags,
        "dry_volume_m3": round(dry_volume, 2),
        "proof": f"({c}/{sum_parts}) × {dry_volume:.2f} m³ × 1440 kg/m³ ÷ 50 kg/bag = {cement_bags} bags"
    }

def calculate_sand_volume(concrete_volume_m3: float, mix_ratio: str = "M20") -> dict:
    ratios = {"M15": (1, 2, 4, 7.0), "M20": (1, 1.5, 3, 5.5), "M25": (1, 1, 2, 4.0)}
    c, s, a, sum_parts = ratios.get(mix_ratio, (1, 1.5, 3, 5.5))
    dry_volume = concrete_volume_m3 * 1.54
    sand_m3 = round((s / sum_parts) * dry_volume, 2)
    return {
        "sand_m3": sand_m3,
        "proof": f"({s}/{sum_parts}) × {dry_volume:.2f} m³ = {sand_m3} m³ fine aggregate"
    }

def calculate_aggregate_volume(concrete_volume_m3: float, mix_ratio: str = "M20") -> dict:
    ratios = {"M15": (1, 2, 4, 7.0), "M20": (1, 1.5, 3, 5.5), "M25": (1, 1, 2, 4.0)}
    c, s, a, sum_parts = ratios.get(mix_ratio, (1, 1.5, 3, 5.5))
    dry_volume = concrete_volume_m3 * 1.54
    aggregate_m3 = round((a / sum_parts) * dry_volume, 2)
    return {
        "aggregate_m3": aggregate_m3,
        "proof": f"({a}/{sum_parts}) × {dry_volume:.2f} m³ = {aggregate_m3} m³ coarse aggregate (20mm)"
    }
