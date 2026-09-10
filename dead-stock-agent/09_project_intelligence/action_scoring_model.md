# Action Scoring Model

The DUST 2 DOLLAR Action Scoring Model provides a transparent, deterministic mathematical framework for ranking candidate dead-stock recovery interventions.

$$\text{Action Score} = w_1 \cdot \text{Demand Opportunity} + w_2 \cdot \text{Aging Urgency} + w_3 \cdot \text{Profit Recovery} + w_4 \cdot \text{Supplier Feasibility} - w_5 \cdot \text{Operational Cost} - w_6 \cdot \text{Brand Risk}$$

## Feature Breakdown

1. **Demand Opportunity ($w_1 = 0.20$)**:
   - Evaluates category velocity, seasonality multipliers, and remaining market elasticity.
2. **Aging Urgency ($w_2 = 0.25$)**:
   - Scaled from days in inventory vs. shelf-life threshold.
   - $> 120\text{ days} \implies 1.0\text{ urgency factor}$.
3. **Profit Recovery Yield ($w_3 = 0.25$)**:
   - Net recovered capital as a percentage of initial acquisition cost ($CP$).
4. **Supplier Feasibility ($w_4 = 0.15$)**:
   - Binary feasibility filter: returns scored $0$ if return window expired; scored $1.0$ if within window minus restocking fee.
5. **Operational Cost ($w_5 = 0.10$)**:
   - Shipping, relabeling, repackaging, or promotional ad-spend.
6. **Brand Risk ($w_6 = 0.05$)**:
   - Protection against excessive price erosion for premium brands.

## Action Priority Tiers
| Score Range | Strategic Action Recommendation | Expected Execution Window |
|---|---|---|
| **85 - 100** | Immediate High-Impact Intervention (e.g. Flash Clearance, Supplier Return) | 24 - 48 Hours |
| **70 - 84** | Targeted Promotion / Bundle Pairing | 3 - 7 Days |
| **50 - 69** | Markdown 10-20% + Channel Reallocation | 1 - 2 Weeks |
| **< 50** | Retain or Liquidate / Write-Off | End of Quarter |
