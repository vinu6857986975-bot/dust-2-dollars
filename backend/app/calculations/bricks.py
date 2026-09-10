"""
Brick and paint calculations from building dimensions.
"""
import math

def calculate_bricks(built_up_area_sqft: float, floors: int = 1, ceiling_height_m: float = 3.0) -> dict:
    area_sqm = built_up_area_sqft * 0.092903
    perimeter_m = 4 * math.sqrt(area_sqm) * 1.35
    wall_height_m = ceiling_height_m * floors
    wall_thickness_m = 0.23  # 9-inch wall
    gross_volume_m3 = perimeter_m * wall_height_m * wall_thickness_m
    net_volume_m3 = round(gross_volume_m3 * 0.85, 2)  # 15% opening deduction
    total_bricks = math.ceil(net_volume_m3 * 500 * 1.05)  # 5% handling wastage
    
    # Mortar 1:6
    mortar_dry_vol = (net_volume_m3 * 0.25) * 1.33
    masonry_cement_bags = math.ceil((1 / 7) * mortar_dry_vol * 1440 / 50)
    masonry_sand_m3 = round((6 / 7) * mortar_dry_vol, 2)
    return {
        "total_bricks": total_bricks,
        "masonry_volume_m3": net_volume_m3,
        "masonry_cement_bags": masonry_cement_bags,
        "masonry_sand_m3": masonry_sand_m3,
        "proof": f"Net Wall Volume = {net_volume_m3:.2f} m³ × 500 bricks/m³ + 5% wastage = {total_bricks:,} Bricks"
    }

def calculate_paint(built_up_area_sqft: float, floors: int = 1) -> dict:
    total_floor_sqft = built_up_area_sqft * floors
    paintable_area_sqft = round(total_floor_sqft * 3.6, 1)
    paint_litres = math.ceil(paintable_area_sqft / 75.0)  # 75 sq.ft / L for 2 coats
    return {
        "paintable_area_sqft": paintable_area_sqft,
        "paint_litres": paint_litres,
        "proof": f"Wall & Ceiling Surface = {paintable_area_sqft} sq.ft ÷ 75 sq.ft/L (2 coats) = {paint_litres} Litres"
    }
