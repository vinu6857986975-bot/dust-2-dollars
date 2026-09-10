"""
DUST 2 DOLLAR — Stock Agent
Analyzes inventory aging, velocity, and risk scoring
"""

from datetime import datetime, date


class StockAgent:
    """
    Analyzes the stock condition of a product.
    Returns a structured StockAnalysis with:
    - Aging score (0-100)
    - Stock velocity
    - Risk level
    - Turnover rate
    - Urgency signals
    """

    URGENCY_THRESHOLDS = {
        "critical": 120,
        "high": 90,
        "medium": 60,
        "low": 30,
    }

    def analyze(self, inventory: dict, product: dict, supplier: dict, rules: list) -> dict:
        """
        Main analysis function.
        :param inventory: inventory row dict
        :param product:   product row dict
        :param supplier:  supplier row dict (can be None)
        :param rules:     list of business_rules dicts
        :return: StockAnalysis dict
        """
        stock_since = self._parse_date(inventory.get("stock_since"))
        last_sale   = self._parse_date(inventory.get("last_sale_date"))
        today       = date.today()

        # ── Core metrics ─────────────────────────────────────
        age_days        = (today - stock_since).days if stock_since else 0
        days_since_sale = (today - last_sale).days   if last_sale  else age_days
        quantity        = int(inventory.get("quantity", 0))
        monthly_sales   = float(inventory.get("monthly_sales", 0))
        cost_price      = float(product.get("cost_price", 0))
        selling_price   = float(product.get("selling_price", 0))
        mrp             = float(product.get("mrp", selling_price))

        # ── Inventory value ───────────────────────────────────
        total_cost_value   = quantity * cost_price
        total_retail_value = quantity * selling_price

        # ── Velocity & turnover ───────────────────────────────
        daily_velocity   = monthly_sales / 30.0 if monthly_sales > 0 else 0.0
        days_to_sellout  = (quantity / daily_velocity) if daily_velocity > 0 else 9999
        turnover_rate    = (monthly_sales / quantity * 100) if quantity > 0 else 0

        # ── Margin info ───────────────────────────────────────
        margin_pct     = ((selling_price - cost_price) / cost_price * 100) if cost_price > 0 else 0
        mrp_headroom   = ((mrp - selling_price) / mrp * 100) if mrp > 0 else 0
        discount_room  = ((selling_price - cost_price) / selling_price * 100) if selling_price > 0 else 0

        # ── Aging score (0-100, higher = more urgent) ─────────
        aging_score = self._calc_aging_score(age_days, days_since_sale)

        # ── Risk level ────────────────────────────────────────
        risk_level  = self._calc_risk(age_days, quantity, monthly_sales, margin_pct)

        # ── Supplier return feasibility ───────────────────────
        return_feasible = False
        return_blocked_reason = ""
        if supplier and supplier.get("return_allowed"):
            window = int(supplier.get("return_window_days", 0))
            if age_days <= window:
                return_feasible = True
            else:
                return_blocked_reason = f"Return window expired ({window} days, stock is {age_days} days old)"
        else:
            return_blocked_reason = "Supplier does not allow returns"

        # ── Dead stock classification ─────────────────────────
        dead_threshold    = self._get_rule_value(rules, "Dead Stock Threshold",    60)
        critical_threshold= self._get_rule_value(rules, "Critical Threshold",     90)

        if age_days >= critical_threshold:
            stock_status = "critical"
        elif age_days >= dead_threshold:
            stock_status = "dead"
        elif age_days >= dead_threshold * 0.5:
            stock_status = "at_risk"
        else:
            stock_status = "healthy"

        # ── Urgency signals ───────────────────────────────────
        signals = []
        if age_days > 90:
            signals.append(f"Stock is {age_days} days old — critical aging")
        if days_since_sale > 30:
            signals.append(f"No sale in {days_since_sale} days — zero demand")
        if quantity > 50:
            signals.append(f"High excess quantity ({quantity} units)")
        if turnover_rate < 5:
            signals.append("Very low inventory turnover rate")
        if total_cost_value > 50000:
            signals.append(f"High capital locked: ₹{total_cost_value:,.0f}")

        return {
            "agent": "StockAgent",
            "status": "ok",
            "metrics": {
                "age_days": age_days,
                "days_since_last_sale": days_since_sale,
                "quantity": quantity,
                "monthly_sales": monthly_sales,
                "daily_velocity": round(daily_velocity, 2),
                "days_to_sellout": round(days_to_sellout, 1),
                "turnover_rate_pct": round(turnover_rate, 2),
                "aging_score": aging_score,
                "risk_level": risk_level,
                "stock_status": stock_status,
            },
            "value": {
                "cost_price": cost_price,
                "selling_price": selling_price,
                "mrp": mrp,
                "total_cost_value": round(total_cost_value, 2),
                "total_retail_value": round(total_retail_value, 2),
                "margin_pct": round(margin_pct, 2),
                "discount_room_pct": round(discount_room, 2),
                "mrp_headroom_pct": round(mrp_headroom, 2),
            },
            "supplier": {
                "return_feasible": return_feasible,
                "return_blocked_reason": return_blocked_reason,
                "supplier_name": supplier.get("name") if supplier else "Unknown",
                "return_window_days": supplier.get("return_window_days", 0) if supplier else 0,
                "refund_type": supplier.get("refund_type", "none") if supplier else "none",
                "penalty_pct": supplier.get("penalty_pct", 0) if supplier else 0,
            },
            "urgency_signals": signals,
        }

    def _calc_aging_score(self, age_days: int, days_since_sale: int) -> int:
        """Composite aging score 0-100"""
        age_score  = min(age_days / 180 * 70, 70)
        sale_score = min(days_since_sale / 90 * 30, 30)
        return min(int(age_score + sale_score), 100)

    def _calc_risk(self, age_days, quantity, monthly_sales, margin_pct) -> str:
        score = 0
        if age_days > 120: score += 40
        elif age_days > 90: score += 30
        elif age_days > 60: score += 20
        elif age_days > 30: score += 10

        if quantity > 100: score += 25
        elif quantity > 50: score += 15
        elif quantity > 20: score += 8

        if monthly_sales < 2: score += 20
        elif monthly_sales < 5: score += 10

        if margin_pct < 10: score += 15

        if score >= 70: return "Critical"
        if score >= 45: return "High"
        if score >= 25: return "Medium"
        return "Low"

    def _get_rule_value(self, rules: list, name: str, default: int) -> int:
        for r in rules:
            if r.get("rule_name") == name and r.get("enabled", 1):
                try:
                    return int(r["rule_value"])
                except Exception:
                    pass
        return default

    def _parse_date(self, date_str):
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except Exception:
                pass
        return None
