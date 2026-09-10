# Risk Model & Assessment

Every dead-stock intervention carries secondary business risks. The Risk Model calculates a composite risk index from 0.0 (Minimal) to 1.0 (Extreme).

## Risk Dimensions
1. **Capital Loss Risk ($R_{\text{loss}}$)**:
   $$\frac{\max(0, \text{Cost Price} - \text{Markdown Price})}{\text{Cost Price}}$$
2. **Channel Conflict / Brand Dilution ($R_{\text{brand}}$)**:
   - High for luxury & premium consumer electronics.
   - Low for generic commodities and seasonal apparel.
3. **Supplier Relationship Impact ($R_{\text{supplier}}$)**:
   - Evaluates frequency of supplier returns against seasonal vendor goodwill limits.
4. **Execution Friction ($R_{\text{exec}}$)**:
   - Warehousing labor for repackaging, bundle tagging, or inter-store freight transfers.

## Risk Classifications
- **LOW (< 0.25)**: Routine automated actions (Promote, Bundle with complimentary item).
- **MEDIUM (0.25 - 0.55)**: 15% - 25% Discount, Vendor credit return.
- **HIGH (> 0.55)**: Flash clearance below cost, wholesale liquidation. Requires manual executive authorization.
