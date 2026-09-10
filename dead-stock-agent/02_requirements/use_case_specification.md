# Use Case Specification: UC-01 Autonomous Analysis

- **Actor:** Inventory Merchandiser
- **Pre-Conditions:** Product SKU exists in the database with inventory and supplier records.
- **Trigger:** User selects "Analyze Product" on the interface.
- **Main Flow:**
  1. Frontend submits POST request to `/api/decision/analyze`.
  2. Orchestrator initializes StockAgent, ProductAgent, StrategyAgent, and DecisionEngine.
  3. StockAgent evaluates age (145 days) and tags as "Dead Stock".
  4. ProductAgent computes margin (40%) and high seasonality risk.
  5. StrategyAgent evaluates 8 actions; detects supplier return window (30d) is exceeded; eliminates "Return to Supplier".
  6. DecisionEngine scores "20% Discount + Bundle" highest (Score: 88).
  7. Frontend renders animated step trace and final recommendation card.
  8. User clicks "Approve".
  9. Decision status updates to "Approved" in the database.
