"""
DUST 2 DOLLAR — Decision Engine
Final decision maker: scores actions, builds composite rank,
calls OpenAI GPT for contextual explanation, outputs structured decision.
"""

import json
import urllib.request
import urllib.error


class DecisionEngine:
    """
    Takes outputs from Stock, Product, Strategy agents.
    Produces the final ranked recommendation with:
    - Composite score
    - Confidence level
    - LLM-generated explanation (OpenAI)
    - Risk assessment
    - Estimated recovery
    """

    def decide(self,
               stock: dict,
               product: dict,
               strategy: dict,
               rules: list,
               openai_key: str = "",
               openai_model: str = "gpt-4o-mini") -> dict:
        """
        Main decision function.
        """
        actions       = strategy.get("actions", [])
        metrics       = stock.get("metrics", {})
        value         = stock.get("value", {})
        prod_profile  = product.get("product_profile", {})
        cat_analysis  = product.get("category_analysis", {})
        demand        = product.get("demand_analysis", {})

        age_days      = metrics.get("age_days", 0)
        aging_score   = metrics.get("aging_score", 0)
        risk_level    = metrics.get("risk_level", "Medium")
        quantity      = metrics.get("quantity", 0)

        # ── Apply composite scoring ───────────────────────────
        scored = []
        for a in actions:
            if not a.get("feasible"):
                continue
            composite = self._composite_score(a, stock, product)
            scored.append({**a, "composite_score": composite})

        scored.sort(key=lambda x: -x["composite_score"])

        if not scored:
            # fallback: include all, even non-feasible
            scored = actions
            scored.sort(key=lambda x: -x.get("score", 0))

        best          = scored[0] if scored else {}
        alternatives  = scored[1:4] if len(scored) > 1 else []

        # ── Confidence ────────────────────────────────────────
        confidence = "High" if aging_score >= 70 else "Medium" if aging_score >= 40 else "Low"

        # ── Estimated recovery ────────────────────────────────
        estimated_recovery = best.get("recovery_estimate", 0)

        # ── Build context for LLM ─────────────────────────────
        context = {
            "product_name":      prod_profile.get("name", ""),
            "sku":               prod_profile.get("sku", ""),
            "category":          prod_profile.get("category", ""),
            "brand":             prod_profile.get("brand", ""),
            "selling_price":     value.get("selling_price", 0),
            "cost_price":        value.get("cost_price", 0),
            "quantity":          quantity,
            "age_days":          age_days,
            "monthly_sales":     metrics.get("monthly_sales", 0),
            "demand_pattern":    demand.get("label", ""),
            "risk_level":        risk_level,
            "seasonality":       cat_analysis.get("seasonality", "none"),
            "is_off_season":     cat_analysis.get("is_off_season", False),
            "best_action":       best.get("action", ""),
            "best_score":        best.get("composite_score", 0),
            "alternatives":      [a.get("action") for a in alternatives],
            "return_feasible":   stock.get("supplier", {}).get("return_feasible", False),
            "urgency_signals":   stock.get("urgency_signals", []),
        }

        # ── LLM Explanation ───────────────────────────────────
        explanation = self._get_llm_explanation(context, openai_key, openai_model)

        # ── Structured decision output ────────────────────────
        return {
            "agent": "DecisionEngine",
            "status": "ok",
            "decision": {
                "recommended_action": best.get("action", "Discount"),
                "composite_score":    round(best.get("composite_score", 0), 1),
                "confidence":         confidence,
                "risk_level":         risk_level,
                "estimated_recovery": round(estimated_recovery, 2),
                "action_params":      best.get("params", {}),
                "action_description": best.get("description", ""),
            },
            "alternatives": [
                {
                    "action":  a.get("action"),
                    "score":   round(a.get("composite_score", a.get("score", 0)), 1),
                    "reason":  a.get("description", ""),
                    "recovery": a.get("recovery_estimate", 0),
                }
                for a in alternatives
            ],
            "explanation":    explanation,
            "all_scores":     [
                {
                    "action":  a.get("action"),
                    "score":   round(a.get("composite_score", a.get("score", 0)), 1),
                    "feasible":a.get("feasible", True),
                }
                for a in (scored if scored else actions)
            ],
        }

    def _composite_score(self, action: dict, stock: dict, product: dict) -> float:
        """
        Composite score = base score + modifiers
        """
        base          = action.get("score", 50)
        urgency_m     = product.get("urgency_modifier", 0)
        season_note   = product.get("category_analysis", {}).get("season_note", "")
        is_off_season = product.get("category_analysis", {}).get("is_off_season", False)

        modifier = 0
        # Boost clearance when off-season
        if is_off_season and action["action"] in ("Clearance Liquidation", "Discount"):
            modifier += 10
        # Boost return to supplier when feasible
        if action["action"] == "Return to Supplier" and action.get("feasible"):
            modifier += 15
        # Boost flash promotion when branded
        if action["action"] == "Flash Promotion" and product.get("strategy_flags", {}).get("is_branded"):
            modifier += 8

        return min(base + modifier + urgency_m * 0.5, 100)

    def _get_llm_explanation(self, context: dict, api_key: str, model: str) -> str:
        """
        Calls OpenAI API for a concise business explanation.
        Falls back to deterministic explanation if no key.
        """
        if not api_key or api_key.strip() == "":
            return self._fallback_explanation(context)

        prompt = f"""You are a senior retail inventory analyst AI.

A retailer has a dead-stock product with the following details:

Product: {context['product_name']} ({context['category']})
Brand: {context['brand']}
SKU: {context['sku']}
Quantity: {context['quantity']} units
Stock Age: {context['age_days']} days
Monthly Sales: {context['monthly_sales']} units/month
Demand Pattern: {context['demand_pattern']}
Seasonality: {context['seasonality']} {'(currently OFF-season)' if context['is_off_season'] else ''}
Cost Price: ₹{context['cost_price']}
Selling Price: ₹{context['selling_price']}
Risk Level: {context['risk_level']}
Supplier Return Available: {'Yes' if context['return_feasible'] else 'No'}

Urgent Signals:
{chr(10).join('- ' + s for s in context['urgency_signals']) if context['urgency_signals'] else '- None critical'}

The AI decision system recommends: **{context['best_action']}** (Score: {context['best_score']}/100)
Alternative options: {', '.join(context['alternatives'])}

Please provide a concise, professional business explanation (3-4 sentences) for WHY this action is the best recommendation. Be specific, reference the data, and give practical advice. Use ₹ for currency."""

        try:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a precise retail inventory decision advisor. Always respond in 3-4 focused sentences."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 200,
                "temperature": 0.5,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return self._fallback_explanation(context) + f" [AI offline: {str(e)[:60]}]"

    def _fallback_explanation(self, ctx: dict) -> str:
        """Rule-based explanation when OpenAI is unavailable."""
        action   = ctx["best_action"]
        product  = ctx["product_name"]
        age      = ctx["age_days"]
        qty      = ctx["quantity"]
        demand   = ctx["demand_pattern"]
        season   = ctx["seasonality"]
        off      = ctx["is_off_season"]

        base = (
            f"{product} has been in stock for {age} days with {qty} units remaining "
            f"and {demand.lower()} demand. "
        )

        if action == "Discount":
            return base + (
                f"A targeted markdown is recommended to stimulate immediate demand and recover capital. "
                f"{'Being off-season, aggressive discounting now prevents deeper losses later. ' if off else ''}"
                f"Monitor sell-through rate weekly and adjust pricing accordingly."
            )
        elif action == "Bundle Deal":
            return base + (
                "Bundling increases perceived value and moves multiple units per transaction, "
                "effectively reducing dead-stock faster while protecting brand positioning. "
                "Consider pairing with complementary products for higher basket size."
            )
        elif action == "Flash Promotion":
            return base + (
                "A time-limited flash promotion creates urgency and can rapidly clear stock "
                "without permanent price erosion. Use social media + in-store signage for maximum reach. "
                "Target 30% of remaining stock in the first 48 hours."
            )
        elif action == "Return to Supplier":
            return base + (
                "Supplier return is the most capital-efficient action — recovering cost with minimal loss. "
                "Initiate the return process immediately while still within the return window. "
                "Document condition and quantities carefully before dispatch."
            )
        elif action == "Clearance Liquidation":
            return base + (
                "With extended aging and very low demand, clearance pricing prioritizes capital recovery over margin. "
                f"{'Seasonal items unsold now will have near-zero value next season. ' if off and season != 'none' else ''}"
                "Price at cost + minimum floor to clear inventory before further value erosion."
            )
        else:
            return base + (
                f"{action} is recommended based on stock age, demand pattern, and business constraints. "
                "Review the action parameters and implement with weekly progress tracking."
            )
