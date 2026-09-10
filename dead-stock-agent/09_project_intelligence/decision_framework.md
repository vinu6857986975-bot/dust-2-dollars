# AnyPortal Decision Framework: Composite Scoring

## The Objective Function
$$\text{CCRS} = \sum_{i=1}^{n} w_i \cdot f_i(x)$$

Where:
- $D_o$ = Demand Opportunity (elasticity vs seasonality) [Weight: 0.20]
- $A_i$ = Inventory Aging Penalty [Weight: 0.25]
- $P_r$ = Profit Recovery Index [Weight: 0.25]
- $S_f$ = Supplier Feasibility Binary [Weight: 0.15]
- $C_o$ = Carrying Cost Deterrence [Weight: 0.15]

## Strategy Ranking Table Example
| Strategy | Raw Score | Feasibility Flag | Final Weighted Rank |
|---|---|---|---|
| 20% Discount + Promo | 88.4 | Feasible | #1 (Recommended) |
| Cross-Category Bundle | 79.2 | Feasible | #2 (Alternative 1) |
| Clearance Liquidation | 64.0 | Feasible | #3 (Alternative 2) |
| Return to Supplier | 0.0 | **BLOCKED (Window Expired)** | Infeasible |
