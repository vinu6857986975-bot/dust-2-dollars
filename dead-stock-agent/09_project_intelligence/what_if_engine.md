# What-If Simulation Engine Specification

The What-If sandbox recalculates strategy scores dynamically as users manipulate four real-time variables:
1. **Discount Depth (%):** Recalculates margin retention vs demand lift.
2. **Elapsed Stock Age (days):** Increases holding cost decay and triggers return window thresholds.
3. **Quantity on Hand:** Triggers bundling feasibility if Qty >= 10.
4. **Supplier Return Window:** Unblocks or blocks supplier return RMA generation.
