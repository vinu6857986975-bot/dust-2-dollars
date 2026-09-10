"""
DUST 2 DOLLAR — Agent Orchestrator
Coordinates all 4 agents:
1. StockAgent      — inventory aging analysis
2. ProductAgent    — product & category analysis
3. StrategyAgent   — candidate action generation
4. DecisionEngine  — final decision + LLM reasoning
"""

import json
import time
from .stock_agent    import StockAgent
from .product_agent  import ProductAgent
from .strategy_agent import StrategyAgent
from .decision_engine import DecisionEngine


class DeadStockOrchestrator:
    """
    Master agent orchestrator.
    Runs the full 4-agent pipeline and returns a complete decision.
    """

    def __init__(self):
        self.stock_agent    = StockAgent()
        self.product_agent  = ProductAgent()
        self.strategy_agent = StrategyAgent()
        self.decision_engine= DecisionEngine()

    def run(self,
            product: dict,
            inventory: dict,
            supplier: dict,
            category: dict,
            rules: list,
            openai_key: str = "",
            openai_model: str = "gpt-4o-mini") -> dict:
        """
        Full pipeline execution.
        Returns structured decision with agent trace.
        """
        trace    = []
        t_start  = time.time()

        def log_step(agent_name: str, result: dict, duration_ms: int):
            trace.append({
                "agent":       agent_name,
                "status":      result.get("status", "ok"),
                "duration_ms": duration_ms,
                "summary":     self._summarize(agent_name, result),
            })

        # ─── Step 1: Stock Agent ──────────────────────────────
        t0 = time.time()
        try:
            stock_result = self.stock_agent.analyze(inventory, product, supplier, rules)
        except Exception as e:
            stock_result = {"agent": "StockAgent", "status": "error", "error": str(e)}
        log_step("Stock Agent", stock_result, int((time.time() - t0) * 1000))

        # ─── Step 2: Product Agent ────────────────────────────
        t0 = time.time()
        try:
            product_result = self.product_agent.analyze(product, category, stock_result)
        except Exception as e:
            product_result = {"agent": "ProductAgent", "status": "error", "error": str(e)}
        log_step("Product Agent", product_result, int((time.time() - t0) * 1000))

        # ─── Step 3: Strategy Agent ───────────────────────────
        t0 = time.time()
        try:
            strategy_result = self.strategy_agent.generate(stock_result, product_result, rules)
        except Exception as e:
            strategy_result = {"agent": "StrategyAgent", "status": "error", "error": str(e)}
        log_step("Strategy Agent", strategy_result, int((time.time() - t0) * 1000))

        # ─── Step 4: Decision Engine ──────────────────────────
        t0 = time.time()
        try:
            decision_result = self.decision_engine.decide(
                stock_result, product_result, strategy_result,
                rules, openai_key, openai_model
            )
        except Exception as e:
            decision_result = {"agent": "DecisionEngine", "status": "error", "error": str(e)}
        log_step("Decision Engine", decision_result, int((time.time() - t0) * 1000))

        total_ms = int((time.time() - t_start) * 1000)

        return {
            "status":    "ok",
            "total_ms":  total_ms,
            "agent_trace": trace,
            "stock":     stock_result,
            "product":   product_result,
            "strategy":  strategy_result,
            "decision":  decision_result,
        }

    def _summarize(self, agent_name: str, result: dict) -> str:
        """Short human-readable summary for each agent step."""
        if result.get("status") == "error":
            return f"Error: {result.get('error', 'unknown')}"

        if agent_name == "Stock Agent":
            m = result.get("metrics", {})
            return (f"Age: {m.get('age_days',0)}d | Qty: {m.get('quantity',0)} | "
                    f"Risk: {m.get('risk_level','?')} | Score: {m.get('aging_score',0)}/100")

        if agent_name == "Product Agent":
            p = result.get("product_profile", {})
            d = result.get("demand_analysis", {})
            c = result.get("category_analysis", {})
            return (f"Category: {p.get('category','?')} | "
                    f"Demand: {d.get('label','?')} | "
                    f"Season: {c.get('seasonality','?')}")

        if agent_name == "Strategy Agent":
            n    = result.get("feasible_count", 0)
            total= result.get("total_actions_evaluated", 0)
            top  = (result.get("actions") or [{}])[0].get("action", "?")
            return f"{n}/{total} feasible actions | Top candidate: {top}"

        if agent_name == "Decision Engine":
            d = result.get("decision", {})
            return (f"Recommended: {d.get('recommended_action','?')} | "
                    f"Score: {d.get('composite_score',0)}/100 | "
                    f"Confidence: {d.get('confidence','?')}")

        return "Completed"
