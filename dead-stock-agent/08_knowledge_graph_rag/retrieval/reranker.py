# -*- coding: utf-8 -*-
"""
Constraint Reranker for Candidate Dead-Stock Actions.
Ranks actions based on profit yield, inventory age urgency, and supplier contract feasibility.
"""
from typing import List, Dict

class ActionReranker:
    @staticmethod
    def rerank(actions: List[Dict], stock_age_days: int, margin_pct: float) -> List[Dict]:
        """
        Adjusts raw heuristic scores with dynamic inventory and margin multipliers.
        """
        for act in actions:
            score = act.get("score", 50)
            action_type = act.get("action", "")

            # If stock age > 120 days, clearance and heavy discounts get prioritized
            if stock_age_days >= 120 and "DISCOUNT" in action_type:
                score += 15
            elif stock_age_days < 60 and "CLEARANCE" in action_type:
                score -= 25

            # Low margin penalizes heavy discounts
            if margin_pct < 0.25 and "DISCOUNT_30" in action_type:
                score -= 30

            act["adjusted_score"] = min(100, max(0, score))

        return sorted(actions, key=lambda x: x.get("adjusted_score", 0), reverse=True)
