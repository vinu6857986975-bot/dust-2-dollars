import time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.orchestrator import DeadStockOrchestrator

orch = DeadStockOrchestrator()
sample_prod = {"name": "Test Item", "cost_price": 1000, "selling_price": 2000, "category": "Apparel"}
sample_inv = {"quantity": 25, "stock_since": "2026-01-01"}
sample_supp = {"return_allowed": 1, "return_window_days": 30}

t0 = time.time()
res = orch.run(sample_prod, sample_inv, sample_supp, {}, [])
elapsed = (time.time() - t0) * 1000
print(f"[Benchmark] Pipeline finished in {elapsed:.2f} ms")
