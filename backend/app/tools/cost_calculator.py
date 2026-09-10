"""
Cost, Supplier Search, Inventory, and Delivery Tools
"""
import math

def calculate_costs(quantities_list: list, price_catalog: dict) -> dict:
    costed = []
    total = 0.0
    for item in quantities_list:
        m_id = item["id"]
        cat = price_catalog.get(m_id, {"price": 100.0})
        unit_price = float(cat.get("price", 100.0))
        subtotal = round(item["quantity"] * unit_price, 2)
        total += subtotal
        costed.append({
            **item,
            "unit_price": unit_price,
            "subtotal": subtotal
        })
    return {
        "costed_materials": costed,
        "total_cost": round(total, 2),
        "currency": "INR"
    }

def rank_suppliers(suppliers: list, materials: list, weights: dict = None) -> dict:
    if not weights:
        weights = {"price": 0.45, "distance": 0.30, "stock": 0.25}
    wp, wd, ws = weights["price"], weights["distance"], weights["stock"]

    ranked = []
    max_dist = max([s.get("distance_km", 10) for s in suppliers] or [15])

    for s in suppliers:
        quote = sum(m["subtotal"] * s.get("multiplier", 1.0) for m in materials)
        price_score = max(0, min(100, 100 - (s.get("multiplier", 1.0) - 0.90) * 250))
        dist_score = max(0, min(100, 100 - (s.get("distance_km", 5) / max_dist) * 100))
        ready_count = s.get("ready_items", len(materials))
        stock_score = (ready_count / max(1, len(materials))) * 100

        composite = round(wp * price_score + wd * dist_score + ws * stock_score, 1)
        ranked.append({
            **s,
            "composite_score": composite,
            "total_quote": round(quote, 2),
            "score_breakdown": {
                "price": round(price_score, 1),
                "distance": round(dist_score, 1),
                "stock": round(stock_score, 1)
            }
        })
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return {
        "ranked_suppliers": ranked,
        "recommended": ranked[0] if ranked else None
    }
