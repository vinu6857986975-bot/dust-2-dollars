# Multi-Agent System Architecture

```
                    ┌─────────────────────────┐
                    │      RETAIL USER        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   ANYPORTAL FRONTEND    │
                    └────────────┬────────────┘
                                 │ HTTP REST
                                 ▼
                    ┌─────────────────────────┐
                    │       BACKEND API       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  ORCHESTRATOR PIPELINE  │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │ Stock Agent  │        │Product Agent │        │Strategy Agent│
  │ • Age Index  │        │ • Elasticity │        │ • 8 Actions  │
  │ • Carrying   │        │ • Margins    │        │ • Raw Scores │
  │   Costs      │        │ • Seasonality│        │              │
  └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  KNOWLEDGE / POLICY RAG │
                    │ • Supplier SLAs & Rules │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    CONSTRAINT ENGINE    │
                    │ • Filter Infeasible     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     DECISION ENGINE     │
                    │ • Multi-Criteria Rank   │
                    │ • Contextual Reasoning  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ HUMAN AUDIT & APPROVAL  │
                    └─────────────────────────┘
```

## Agent Role Taxonomy

### 1. Stock Agent
- **Duty:** Quantify inventory stagnation without bias.
- **Formulas:**
  $$\text{Age} = \text{Days since received}$$
  $$\text{Holding Cost Drain} = \text{Qty} \times \text{Unit Cost} \times 0.015 \times (\text{Age}/30)$$
  $$\text{Velocity Score} = \max(0, 100 - \text{Age} \times 0.6)$$

### 2. Product Agent
- **Duty:** Determine commercial characteristics of the item.
- **Evaluates:** Gross margin %, brand equity level, category price sensitivity, and current seasonal relevance.

### 3. Strategy Agent
- **Duty:** Generate all 8 candidate actions:
  `DISCOUNT`, `BUNDLE`, `PROMOTE`, `RETURN_SUPPLIER`, `CLEARANCE`, `RELOCATE`, `DONATE`, `REPACKAGE`.

### 4. Constraint & Knowledge Gate
- **Duty:** Guarantee policy adherence before LLM synthesis.
- **Rule:** If `stock_age > supplier.return_window_days`, eliminate `RETURN_SUPPLIER` immediately.

### 5. Decision Engine
- **Duty:** Calculate Composite Capital Recovery Score (CCRS) and synthesize clear executive guidance.
