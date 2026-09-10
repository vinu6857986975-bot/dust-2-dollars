"""
Construct-AI - Deterministic Calculation Engine
Rule 2.1: The LLM NEVER performs engineering calculations or pricing arithmetic directly.
All quantity math is executed by these deterministic, auditable, and reproducible Python functions.
"""

import math

def calculate_concrete_volume(built_up_area_sqft, floors=1, building_type="residential"):
    """
    Calculates total concrete volume (m³) required for slabs, beams, columns, and foundations.
    IS 456 standard empirical estimation for RCC structures.
    """
    area_sqm = built_up_area_sqft * 0.092903
    total_built_up_sqm = area_sqm * floors
    
    # Concrete index per square meter of built-up area:
    # Residential: ~0.20 - 0.24 m³ concrete per m² built-up area
    # Commercial: ~0.25 - 0.30 m³ concrete per m² built-up area
    factor = 0.22 if building_type.lower() == "residential" else 0.28
    concrete_volume_m3 = round(total_built_up_sqm * factor, 2)
    
    return {
        "built_up_area_sqm": round(total_built_up_sqm, 2),
        "concrete_volume_m3": concrete_volume_m3,
        "calculation_proof": f"{total_built_up_sqm:.2f} m² total area × {factor} m³/m² (IS 456 empirical factor) = {concrete_volume_m3:.2f} m³"
    }

def calculate_cement_sand_aggregate(concrete_volume_m3, mix_ratio="M20"):
    """
    Calculates Cement (bags), Sand (m³), and Coarse Aggregate (m³)
    using standard dry volume coefficient 1.54.
    M20 mix = 1 : 1.5 : 3 (Sum = 5.5)
    M25 mix = 1 : 1 : 2   (Sum = 4.0)
    1 m³ cement = 1440 kg = 28.8 bags (50 kg each)
    """
    ratios = {
        "M15": (1, 2, 4, 7.0),
        "M20": (1, 1.5, 3, 5.5),
        "M25": (1, 1, 2, 4.0)
    }
    c_part, s_part, a_part, sum_parts = ratios.get(mix_ratio, (1, 1.5, 3, 5.5))
    
    # Dry volume conversion
    dry_volume = concrete_volume_m3 * 1.54
    
    # Cement
    cement_volume_m3 = (c_part / sum_parts) * dry_volume
    cement_kg = cement_volume_m3 * 1440
    cement_bags = math.ceil(cement_kg / 50)
    
    # Sand (Fine aggregate)
    sand_m3 = round((s_part / sum_parts) * dry_volume, 2)
    
    # Coarse Aggregate
    aggregate_m3 = round((a_part / sum_parts) * dry_volume, 2)
    
    return {
        "mix_ratio": mix_ratio,
        "dry_volume_m3": round(dry_volume, 2),
        "cement_bags": cement_bags,
        "sand_m3": sand_m3,
        "aggregate_m3": aggregate_m3,
        "calculation_proof": f"Dry Volume = {concrete_volume_m3:.2f} × 1.54 = {dry_volume:.2f} m³. Mix {mix_ratio} (1:{s_part}:{a_part}). Cement: ({c_part}/{sum_parts})×{dry_volume:.2f}×1440/50 = {cement_bags} bags. Sand: {sand_m3} m³. Aggregate: {aggregate_m3} m³."
    }

def calculate_steel_requirement(concrete_volume_m3, building_type="residential"):
    """
    Estimates Steel reinforcement (TMT Fe550) in Tonnes and Kilograms.
    Civil thumb rule:
    Slabs: ~1% steel of concrete volume
    Beams: ~1.5% - 2% steel
    Columns: ~2.5% steel
    Average residential structure: ~82 kg steel per m³ concrete (steel density = 7850 kg/m³)
    Commercial structure: ~96 kg steel per m³ concrete
    """
    kg_per_m3 = 82 if building_type.lower() == "residential" else 96
    total_steel_kg = round(concrete_volume_m3 * kg_per_m3, 2)
    total_steel_tonnes = round(total_steel_kg / 1000.0, 3)
    
    return {
        "steel_kg": total_steel_kg,
        "steel_tonnes": total_steel_tonnes,
        "kg_per_m3": kg_per_m3,
        "calculation_proof": f"{concrete_volume_m3:.2f} m³ concrete × {kg_per_m3} kg/m³ = {total_steel_kg:.2f} kg ({total_steel_tonnes:.3f} Tonnes Fe550 Grade)"
    }

def calculate_brickwork(built_up_area_sqft, floors=1, ceiling_height_m=3.0):
    """
    Estimates standard red clay bricks (or modular AAC blocks).
    Standard modular brick with mortar: 20cm × 10cm × 10cm.
    Approx 500 bricks required per m³ of brick masonry.
    """
    area_sqm = built_up_area_sqft * 0.092903
    perimeter_m = 4 * math.sqrt(area_sqm) * 1.35  # perimeter + internal partitions
    wall_height_m = ceiling_height_m * floors
    wall_thickness_m = 0.23  # 9-inch load-bearing / external wall
    
    gross_wall_volume_m3 = perimeter_m * wall_height_m * wall_thickness_m
    net_wall_volume_m3 = gross_wall_volume_m3 * 0.85  # Deduct 15% for doors & windows
    
    raw_bricks = net_wall_volume_m3 * 500
    total_bricks = math.ceil(raw_bricks * 1.05)  # 5% wastage
    
    # Mortar cement & sand for brickwork (1:6 mix)
    mortar_dry_vol = (net_wall_volume_m3 * 0.25) * 1.33
    masonry_cement_bags = math.ceil((1 / 7) * mortar_dry_vol * 1440 / 50)
    masonry_sand_m3 = round((6 / 7) * mortar_dry_vol, 2)
    
    return {
        "total_bricks": total_bricks,
        "masonry_volume_m3": round(net_wall_volume_m3, 2),
        "masonry_cement_bags": masonry_cement_bags,
        "masonry_sand_m3": masonry_sand_m3,
        "calculation_proof": f"Net Wall Volume = {net_wall_volume_m3:.2f} m³ × 500 bricks/m³ + 5% wastage = {total_bricks} bricks"
    }

def calculate_finishing(built_up_area_sqft, floors=1):
    """
    Estimates Vitrified Flooring Tiles (sq.ft) and Wall Paint (Litres).
    Flooring = Built-up area + 8% cutting and breakage.
    Paint = 3.6 × Floor Area (Walls + Ceiling), primer + 2 coats interior emulsion.
    Average coverage: 1 Litre covers ~75 sq.ft for 2 coats.
    """
    total_floor_sqft = built_up_area_sqft * floors
    tiles_sqft = math.ceil(total_floor_sqft * 1.08)
    
    paintable_area_sqft = total_floor_sqft * 3.6
    paint_litres = math.ceil(paintable_area_sqft / 75.0)
    
    return {
        "tiles_sqft": tiles_sqft,
        "paintable_area_sqft": round(paintable_area_sqft, 2),
        "paint_litres": paint_litres,
        "calculation_proof": f"Tiles: {total_floor_sqft} sq.ft × 1.08 = {tiles_sqft} sq.ft. Paint: {paintable_area_sqft:.1f} sq.ft wall area ÷ 75 sq.ft/L (2 coats) = {paint_litres} Litres."
    }
