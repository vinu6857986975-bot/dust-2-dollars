# Confidence Model & Uncertainty Quantification

DUST 2 DOLLAR assigns a dynamic confidence score ($C \in [0.0, 1.0]$) to every generated recommendation.

## Confidence Formula
$$C = 0.40 \cdot C_{\text{data}} + 0.35 \cdot C_{\text{constraint}} + 0.25 \cdot C_{\text{agent\_agreement}}$$

### Components
1. **$C_{\text{data}}$ — Data Completeness**:
   - Checks presence of SKU, cost price, selling price, supplier contract, stock timestamp, and sales velocity.
2. **$C_{\text{constraint}}$ — Constraint Alignment**:
   - Assesses distance from hard boundaries (e.g. stock age vs. return cut-off).
3. **$C_{\text{agent\_agreement}}$ — Inter-Agent Consensus**:
   - Measures convergence between Stock Agent diagnostics, Product Agent margin checks, and Strategy Agent proposals.

### Threshold Actions
- **$C \ge 0.85$**: High Confidence. Autonomously queueable with 1-click execution.
- **$0.70 \le C < 0.85$**: Medium Confidence. Standard human review recommended.
- **$C < 0.70$**: Low Confidence. Flagged for manual merchandise manager inspection.
