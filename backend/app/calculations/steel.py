"""
Preliminary steel reinforcement estimate using configured project assumptions.
Standard: IS 1786 Fe550 High-Yield Deformed Bars
"""

def calculate_steel_requirement(concrete_volume_m3: float, building_type: str = "residential") -> dict:
    kg_per_m3 = 82.0 if building_type.lower() == "residential" else 96.0
    total_steel_kg = round(concrete_volume_m3 * kg_per_m3, 2)
    total_steel_tonnes = round(total_steel_kg / 1000.0, 3)
    return {
        "steel_kg": total_steel_kg,
        "steel_tonnes": total_steel_tonnes,
        "reinforcement_density_kg_m3": kg_per_m3,
        "proof": f"{concrete_volume_m3:.2f} m³ concrete × {kg_per_m3} kg/m³ = {total_steel_kg:.2f} kg ({total_steel_tonnes:.3f} Tonnes Fe550 Grade)"
    }
