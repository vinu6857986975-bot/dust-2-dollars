"""
Concrete volume calculations based on supplied dimensions/assumptions.
Standard: IS 456:2000
"""

def calculate_concrete_volume(built_up_area_sqft: float, floors: int = 1, building_type: str = "residential") -> dict:
    area_sqm = built_up_area_sqft * 0.092903
    total_built_up_sqm = area_sqm * floors
    factor = 0.22 if building_type.lower() == "residential" else 0.28
    volume_m3 = round(total_built_up_sqm * factor, 2)
    return {
        "built_up_area_sqm": round(total_built_up_sqm, 2),
        "concrete_volume_m3": volume_m3,
        "empirical_factor": factor,
        "proof": f"{total_built_up_sqm:.2f} m² × {factor} m³/m² = {volume_m3:.2f} m³ concrete"
    }
