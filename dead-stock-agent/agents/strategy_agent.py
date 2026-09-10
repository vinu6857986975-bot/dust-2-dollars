"""
DUST 2 DOLLAR — Strategy Agent
Generates all feasible candidate actions with preliminary scores.
Applies hard business constraint filtering.
"""


class StrategyAgent:
    """
    Generates candidate actions for a dead-stock product.

    Actions considered:
    1. Discount (markdown)
    2. Bundle Deal
    3. Promote (flash sale / social media)
    4. Return to Supplier
    5. Clearance / Liquidation
    6. Relocate to Better Location
    7. Donation / Write-off
    8. Repackage / Reposition
    """

    ACTIONS = [
        "Discount",
        "Bundle Deal",
        "Flash Promotion",
        "Return to Supplier",
        "Clearance Liquidation",
        "Relocate",
        "Donate / Write-off",
        "Repackage & Reposition",
    ]

    def generate(self, stock: dict, product: dict, rules: list) -> dict:
        """
        :param stock:   StockAgent output
        :param product: ProductAgent output
        :param rules:   business rules list
        :return: StrategyAnalysis dict with scored + filtered actions
        """
        metrics    = stock.get("metrics", {})
        value      = stock.get("value", {})
        supplier   = stock.get("supplier", {})
        flags      = product.get("strategy_flags", {})
        urgency_m  = product.get("urgency_modifier", 0)

        age_days       = metrics.get("age_days", 0)
        quantity       = metrics.get("quantity", 0)
        aging_score    = metrics.get("aging_score", 0)
        margin_pct     = value.get("margin_pct", 0)
        discount_room  = value.get("discount_room_pct", 0)
        selling_price  = value.get("selling_price", 0)
        cost_price     = value.get("cost_price", 0)

        max_discount   = self._get_rule(rules, "Maximum Discount Cap", 50)
        min_discount   = self._get_rule(rules, "Minimum Discount Cap", 10)
        clearance_floor= self._get_rule(rules, "Clearance Margin Floor", 5)

        actions = []

        # ── 1. Discount ───────────────────────────────────────
        if discount_room >= min_discount:
            disc_pct   = min(int(aging_score * 0.5), max_discount)
            disc_pct   = max(disc_pct, min_discount)
            disc_price = selling_price * (1 - disc_pct / 100)
            still_profit = disc_price > cost_price * (1 + clearance_floor / 100)
            score = self._discount_score(age_days, quantity, discount_room, urgency_m)
            actions.append({
                "action": "Discount",
                "feasible": still_profit,
                "blocked_reason": "" if still_profit else "Discount would go below cost floor",
                "score": score,
                "params": {
                    "suggested_discount_pct": disc_pct,
                    "new_price": round(disc_price, 2),
                    "profit_per_unit": round(disc_price - cost_price, 2),
                },
                "description": f"Apply {disc_pct}% markdown — new price ₹{disc_price:,.0f}",
                "recovery_estimate": round((disc_price - cost_price) * quantity, 2),
                "risk": "Low" if disc_pct <= 25 else "Medium",
            })

        # ── 2. Bundle Deal ────────────────────────────────────
        bundle_ok = flags.get("bundle_suitable") and quantity >= 10
        actions.append({
            "action": "Bundle Deal",
            "feasible": bundle_ok,
            "blocked_reason": "" if bundle_ok else "Qty < 10 or category not suitable for bundling",
            "score": self._bundle_score(age_days, quantity, flags) if bundle_ok else 20,
            "params": {"bundle_size": 2 if quantity < 30 else 3},
            "description": "Bundle 2-3 units at discounted combo price to increase perceived value",
            "recovery_estimate": round((selling_price * 0.85 - cost_price) * quantity, 2) if bundle_ok else 0,
            "risk": "Low",
        })

        # ── 3. Flash Promotion ────────────────────────────────
        promo_ok = flags.get("promo_suitable") and selling_price >= 500
        actions.append({
            "action": "Flash Promotion",
            "feasible": promo_ok,
            "blocked_reason": "" if promo_ok else "Price < ₹500 or category not promotion-friendly",
            "score": self._promo_score(age_days, selling_price, flags) if promo_ok else 25,
            "params": {"channels": ["Social Media", "Email", "In-store"]},
            "description": "48-hour flash sale or social media promotion to drive rapid demand",
            "recovery_estimate": round((selling_price * 0.9 - cost_price) * quantity * 0.3, 2) if promo_ok else 0,
            "risk": "Low",
        })

        # ── 4. Return to Supplier ─────────────────────────────
        return_ok = supplier.get("return_feasible", False)
        penalty   = float(supplier.get("penalty_pct", 0))
        refund_type = supplier.get("refund_type", "none")
        net_recovery = cost_price * (1 - penalty / 100) * quantity
        actions.append({
            "action": "Return to Supplier",
            "feasible": return_ok,
            "blocked_reason": supplier.get("return_blocked_reason", ""),
            "score": self._return_score(return_ok, penalty, age_days) if return_ok else 10,
            "params": {
                "penalty_pct": penalty,
                "refund_type": refund_type,
                "net_recovery": round(net_recovery, 2),
            },
            "description": f"Return to {supplier.get('supplier_name','supplier')} — {refund_type} refund with {penalty}% penalty",
            "recovery_estimate": round(net_recovery, 2) if return_ok else 0,
            "risk": "Very Low" if penalty == 0 else "Low",
        })

        # ── 5. Clearance Liquidation ──────────────────────────
        clear_price  = cost_price * (1 + clearance_floor / 100)
        clear_feasible = clear_price < selling_price * 0.6
        actions.append({
            "action": "Clearance Liquidation",
            "feasible": True,
            "blocked_reason": "",
            "score": self._clearance_score(age_days, quantity, margin_pct),
            "params": {
                "clearance_price": round(clear_price, 2),
                "discount_vs_mrp": round((1 - clear_price / value.get("mrp", selling_price)) * 100, 1),
            },
            "description": f"Clearance sale at ₹{clear_price:,.0f} — recover cost + {clearance_floor}% margin",
            "recovery_estimate": round((clear_price - cost_price) * quantity, 2),
            "risk": "High",
        })

        # ── 6. Relocate ───────────────────────────────────────
        relocate_ok = flags.get("relocate_suitable") and quantity >= 5
        actions.append({
            "action": "Relocate",
            "feasible": relocate_ok,
            "blocked_reason": "" if relocate_ok else "Category not suitable for relocation strategy",
            "score": self._relocate_score(age_days) if relocate_ok else 15,
            "params": {"target_location": "High-traffic display shelf"},
            "description": "Move to prime display location or higher-footfall store section",
            "recovery_estimate": round((selling_price - cost_price) * quantity * 0.2, 2) if relocate_ok else 0,
            "risk": "Very Low",
        })

        # ── 7. Donate / Write-off ─────────────────────────────
        actions.append({
            "action": "Donate / Write-off",
            "feasible": True,
            "blocked_reason": "",
            "score": 15 if age_days > 150 else 5,
            "params": {"tax_benefit": True},
            "description": "Donate to NGO/charity for CSR benefit + tax write-off. Last resort.",
            "recovery_estimate": 0,
            "risk": "None",
        })

        # ── 8. Repackage ──────────────────────────────────────
        repack_ok = not flags.get("is_perishable") and selling_price >= 800
        actions.append({
            "action": "Repackage & Reposition",
            "feasible": repack_ok,
            "blocked_reason": "" if repack_ok else "Perishable or low-value item",
            "score": 35 if repack_ok else 5,
            "params": {"new_label": "Gift Set Edition"},
            "description": "Repackage as gift set or premium edition to justify price",
            "recovery_estimate": round((selling_price * 1.1 - cost_price) * quantity * 0.15, 2) if repack_ok else 0,
            "risk": "Medium",
        })

        # ── Sort by score (feasible first) ────────────────────
        actions.sort(key=lambda a: (0 if a["feasible"] else 1, -a["score"]))

        return {
            "agent": "StrategyAgent",
            "status": "ok",
            "total_actions_evaluated": len(actions),
            "feasible_count": sum(1 for a in actions if a["feasible"]),
            "actions": actions,
        }

    # ── Scoring helpers ───────────────────────────────────────

    def _discount_score(self, age_days, qty, discount_room, urgency_m):
        s  = min(age_days / 180 * 40, 40)
        s += min(qty / 100 * 20, 20)
        s += min(discount_room / 50 * 25, 25)
        s += urgency_m
        return min(int(s + 10), 95)

    def _bundle_score(self, age_days, qty, flags):
        s = 30
        if age_days > 90: s += 20
        if qty > 30: s += 15
        if flags.get("is_branded"): s += 10
        return min(s, 80)

    def _promo_score(self, age_days, price, flags):
        s = 40
        if age_days > 60: s += 15
        if price >= 1500: s += 10
        if flags.get("is_branded"): s += 10
        return min(s, 85)

    def _return_score(self, feasible, penalty, age_days):
        if not feasible: return 5
        s = 70
        s -= penalty * 1.5
        if age_days < 30: s += 10
        return max(int(s), 20)

    def _clearance_score(self, age_days, qty, margin_pct):
        s = 20
        if age_days > 120: s += 30
        elif age_days > 90: s += 20
        if qty > 50: s += 15
        if margin_pct > 40: s += 15
        return min(s, 75)

    def _relocate_score(self, age_days):
        if age_days > 90: return 45
        if age_days > 60: return 35
        return 25

    def _get_rule(self, rules, name, default):
        for r in rules:
            if r.get("rule_name") == name and r.get("enabled", 1):
                try:
                    return float(r["rule_value"])
                except Exception:
                    pass
        return default
