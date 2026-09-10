# Methodology & Agentic Pipeline

The DUST 2 DOLLAR methodology rejects brittle, end-to-end black-box models in favor of a layered, verifiable agentic workflow:

```
[ Ingest Inventory & Supplier Data ]
                 ↓
        [ Stock Agent ] ──> Analyzes aging curves & holding cost trajectory
                 ↓
       [ Product Agent ] ──> Computes gross margins, velocity drop, category flags
                 ↓
      [ Strategy Agent ] ──> Synthesizes candidate interventions
                 ↓
  [ Knowledge Graph / RAG ] ──> Injects supplier return windows & price rules
                 ↓
   [ Constraint Engine ] ──> Deterministically filters infeasible actions (Hard Block)
                 ↓
    [ Decision Engine ] ──> Multi-objective scoring & LLM contextual reasoning
                 ↓
   [ Human Approval ] ──> Interactive Retailer Dashboard (Approve/Reject/Override)
                 ↓
   [ Immutable Audit ] ──> Persisted to decision ledger
```

## Agent Specialization
- **Stock Agent**: Calculates $\text{Holding Cost} = \text{Cost} \times \text{Daily Holding Rate} \times \text{Days}$.
- **Product Agent**: Determines margin headroom $\text{Margin} = \frac{\text{Selling Price} - \text{Cost Price}}{\text{Selling Price}}$.
- **Strategy Agent**: Formulates 5 distinct strategic archetypes:
  1. Return to Supplier (Vendor Credit)
  2. Targeted Promotional Push (5-10% discount + advertising)
  3. Dynamic Markdown (15-30% discount)
  4. Curated Bundle Pairing (Dead item + High-velocity item)
  5. Flash Clearance / Liquidation
- **Constraint Engine**: Eliminates any candidate action violating contractual return windows or negative margins.
