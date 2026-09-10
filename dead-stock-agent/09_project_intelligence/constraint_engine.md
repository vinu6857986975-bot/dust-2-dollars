# Constraint Engine Architecture

The DUST 2 DOLLAR Constraint Engine acts as an impenetrable programmatic boundary between probabilistic LLM outputs and real-world business execution.

```
                    Raw Candidate Actions
                             │
                             ▼
                 [ Hard Filter: Return Policy ]
                             │
            Passed ──────────┴────────── Failed ───> Tag INFEASIBLE
              │
              ▼
                 [ Hard Filter: Margin Floor ]
                             │
            Passed ──────────┴────────── Failed ───> Clamp to Floor
              │
              ▼
                 [ Hard Filter: Stock Age ]
                             │
            Passed ──────────┴────────── Failed ───> Suppress Discount
              │
              ▼
                 [ Soft Filter: Action Scoring ]
                             │
                             ▼
                 Ranked Feasible Interventions
```

## Algorithmic Guarantees
1. **Zero Hallucinated Returns**: Regardless of LLM suggestion, if contract dates do not permit returns, the engine forcefully excludes supplier return actions.
2. **Deterministic Clamping**: Every suggested percentage discount is strictly bounded by contractual minimum price floors.
3. **Audit Trail Verification**: Every filter evaluation generates a deterministic trace record logged directly into the decision payload.
