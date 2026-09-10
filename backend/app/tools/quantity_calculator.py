"""
Shared Deterministic Quantity Calculator Tool
Rule 2.1: LLM Does Not Calculate
"""
from backend.app.calculations.concrete import calculate_concrete_volume
from backend.app.calculations.cement import calculate_cement_bags, calculate_sand_volume, calculate_aggregate_volume
from backend.app.calculations.steel import calculate_steel_requirement
from backend.app.calculations.bricks import calculate_bricks, calculate_paint

def compute_project_quantities(floor_area_sqft: float, floors: int = 1, building_type: str = "residential") -> dict:
    concrete = calculate_concrete_volume(floor_area_sqft, floors, building_type)
    c_vol = concrete["concrete_volume_m3"]
    
    cement = calculate_cement_bags(c_vol, "M20")
    sand = calculate_sand_volume(c_vol, "M20")
    aggregate = calculate_aggregate_volume(c_vol, "M20")
    steel = calculate_steel_requirement(c_vol, building_type)
    bricks = calculate_bricks(floor_area_sqft, floors)
    paint = calculate_paint(floor_area_sqft, floors)
    
    total_cement = cement["cement_bags"] + bricks["masonry_cement_bags"]
    total_sand = round(sand["sand_m3"] + bricks["masonry_sand_m3"], 2)
    tiles_sqft = round(floor_area_sqft * floors * 1.08)

    return {
        "concrete_volume_m3": c_vol,
        "cement_bags": total_cement,
        "sand_m3": total_sand,
        "aggregate_m3": aggregate["aggregate_m3"],
        "steel_tonnes": steel["steel_tonnes"],
        "bricks_nos": bricks["total_bricks"],
        "tiles_sqft": tiles_sqft,
        "paint_litres": paint["paint_litres"],
        "proofs": {
            "concrete": concrete["proof"],
            "cement": cement["proof"],
            "sand": sand["proof"],
            "aggregate": aggregate["proof"],
            "steel": steel["proof"],
            "bricks": bricks["proof"],
            "paint": paint["proof"]
        }
    }
