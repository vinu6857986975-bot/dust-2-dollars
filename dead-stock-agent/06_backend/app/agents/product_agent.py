"""
DUST 2 DOLLAR — Product Agent
Analyzes product characteristics, category seasonality,
demand patterns, and product-level strategic fit.
"""


class ProductAgent:
    """
    Analyzes product-level attributes to inform strategy.
    Returns a ProductAnalysis with:
    - Category type and seasonality flags
    - Price tier
    - Demand pattern
    - Product-level constraints
    """

    PRICE_TIERS = [
        (500,  "Budget"),
        (1500, "Economy"),
        (3000, "Mid-range"),
        (7000, "Premium"),
        (float("inf"), "Luxury"),
    ]

    SEASONAL_MAP = {
        "winter":  {"peak_months": [11, 12, 1, 2], "off_months": [5, 6, 7, 8]},
        "summer":  {"peak_months": [4, 5, 6, 7],   "off_months": [11, 12, 1, 2]},
        "festive": {"peak_months": [9, 10, 11],     "off_months": [2, 3, 4, 5]},
        "monsoon": {"peak_months": [6, 7, 8, 9],    "off_months": [11, 12, 1, 2]},
        "none":    {"peak_months": list(range(1,13)), "off_months": []},
    }

    def analyze(self, product: dict, category: dict, stock_analysis: dict) -> dict:
        """
        :param product:        product row dict
        :param category:       category row dict (can be None)
        :param stock_analysis: output from StockAgent
        :return: ProductAnalysis dict
        """
        import datetime
        current_month = datetime.date.today().month

        category_name      = (category or {}).get("name", "General")
        seasonality        = (category or {}).get("seasonality", "none")
        avg_shelf_days     = int((category or {}).get("avg_shelf_days", 90))
        dead_threshold     = int((category or {}).get("dead_threshold_days", 60))

        selling_price = float(product.get("selling_price", 0))
        cost_price    = float(product.get("cost_price", 0))
        brand         = product.get("brand", "Unknown")

        # ── Price tier ────────────────────────────────────────
        price_tier = "Mid-range"
        for threshold, tier in self.PRICE_TIERS:
            if selling_price <= threshold:
                price_tier = tier
                break

        # ── Seasonality analysis ──────────────────────────────
        seasonal_info   = self.SEASONAL_MAP.get(seasonality, self.SEASONAL_MAP["none"])
        is_peak_season  = current_month in seasonal_info["peak_months"]
        is_off_season   = current_month in seasonal_info["off_months"]
        season_penalty  = 0
        season_note     = ""

        if seasonality != "none":
            if is_off_season:
                season_penalty = 20
                season_note    = f"Currently OFF-SEASON for {seasonality} products — urgent action needed"
            elif is_peak_season:
                season_penalty = -10  # bonus (still sellable)
                season_note    = f"Currently PEAK SEASON for {seasonality} products — opportunity window"

        # ── Demand pattern ────────────────────────────────────
        monthly_sales  = float(stock_analysis.get("metrics", {}).get("monthly_sales", 0))
        if monthly_sales == 0:
            demand_pattern = "no_demand"
            demand_label   = "No Demand"
        elif monthly_sales < 3:
            demand_pattern = "very_slow"
            demand_label   = "Very Slow Moving"
        elif monthly_sales < 10:
            demand_pattern = "slow"
            demand_label   = "Slow Moving"
        elif monthly_sales < 30:
            demand_pattern = "moderate"
            demand_label   = "Moderate Moving"
        else:
            demand_pattern = "fast"
            demand_label   = "Fast Moving"

        # ── Bundle suitability ────────────────────────────────
        bundle_suitable = (
            selling_price <= 2000 and
            stock_analysis.get("metrics", {}).get("quantity", 0) >= 10 and
            category_name in ("Apparel", "Footwear", "Beauty & Personal Care", "Books & Stationery", "Grocery")
        )

        # ── Promotion suitability ─────────────────────────────
        promo_suitable = (
            selling_price >= 500 and
            category_name in ("Electronics", "Apparel", "Footwear", "Sports & Fitness", "Toys & Games")
        )

        # ── Relocation suitability ────────────────────────────
        relocate_suitable = (
            category_name in ("Apparel", "Footwear", "Electronics", "Toys & Games")
        )

        # ── Product score addition ────────────────────────────
        product_urgency_modifier = season_penalty

        return {
            "agent": "ProductAgent",
            "status": "ok",
            "product_profile": {
                "name": product.get("name"),
                "sku": product.get("sku"),
                "brand": brand,
                "category": category_name,
                "price_tier": price_tier,
                "selling_price": selling_price,
                "cost_price": cost_price,
            },
            "category_analysis": {
                "seasonality": seasonality,
                "is_peak_season": is_peak_season,
                "is_off_season": is_off_season,
                "avg_shelf_days": avg_shelf_days,
                "category_dead_threshold": dead_threshold,
                "season_note": season_note,
                "season_urgency_modifier": season_penalty,
            },
            "demand_analysis": {
                "pattern": demand_pattern,
                "label": demand_label,
                "monthly_sales": monthly_sales,
            },
            "strategy_flags": {
                "bundle_suitable": bundle_suitable,
                "promo_suitable": promo_suitable,
                "relocate_suitable": relocate_suitable,
                "is_perishable": category_name in ("Grocery",),
                "is_high_value": selling_price >= 3000,
                "is_branded": bool(brand and brand not in ("Unknown", "")),
            },
            "urgency_modifier": product_urgency_modifier,
        }
