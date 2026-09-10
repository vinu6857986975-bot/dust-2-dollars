# Business Rules Specification

Deterministic retail constraints enforce business integrity across all automated dead-stock recovery actions.

## Active System Rules

### BR-01: Supplier Return Window Enforcement (Priority 100)
- **Constraint**: No product may be recommended for supplier return if `inventory.age_days > supplier.return_window_days`.
- **Enforcement**: Hard blocker (`FEASIBILITY = INFEASIBLE`).

### BR-02: Minimum Price Floor Protection (Priority 90)
- **Constraint**: Promotional markdowns cannot reduce selling price below 70% of Cost Price ($CP \times 0.70$), unless explicit user clearance override is granted.
- **Enforcement**: Mathematical clamping.

### BR-03: Fresh Stock Immunity (Priority 85)
- **Constraint**: Items with `age_days < 45` are categorized as Active/Healthy Inventory. Automated clearance and supplier returns are disabled.
- **Enforcement**: Status bypass.

### BR-04: High-Value Liquidation Guardrail (Priority 95)
- **Constraint**: Single SKU batches with total capital value $> \$10,000$ (₹500,000) require secondary human approval before automated markdowns trigger.
- **Enforcement**: Approval state set to `PENDING_SUPERVISOR`.

### BR-05: Category Perishability & Seasonal Cutoffs (Priority 80)
- **Constraint**: Seasonal apparel (e.g. Winter Jackets in March) automatically receive an aging multiplier increase of $+1.5\times$ to prevent multi-season obsolescence.
