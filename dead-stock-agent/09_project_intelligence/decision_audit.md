# Decision Audit & Governance Protocol

All automated recommendations and human resolutions in DUST 2 DOLLAR produce immutable, tamper-evident audit logs.

## Audit Entry Schema
```json
{
  "decision_id": 104,
  "timestamp": "2026-09-09T14:40:00Z",
  "product_id": 1,
  "sku": "JKT-WIN-001",
  "input_metrics": {
    "age_days": 145,
    "quantity": 42,
    "cost_value": 63000.0,
    "supplier_return_window_days": 30
  },
  "constraint_evaluations": [
    { "rule": "BR-01", "result": "FAIL (145d > 30d)", "action_impact": "SUPPLIER_RETURN BLOCKED" },
    { "rule": "BR-02", "result": "PASS", "action_impact": "PRICE_FLOOR_VALID" }
  ],
  "agent_scores": {
    "DISCOUNT_20": 87.5,
    "BUNDLE": 71.0,
    "PROMOTE": 78.0,
    "SUPPLIER_RETURN": 0.0
  },
  "recommended_action": "DISCOUNT_20",
  "user_resolution": {
    "status": "APPROVED",
    "user_id": "manager_admin",
    "resolved_at": "2026-09-09T14:42:00Z",
    "override_notes": null
  }
}
```

## Governance Guarantees
- Every decision has bidirectional traceability to product inventory and supplier contract versions.
- Decisions cannot be deleted from the audit ledger.
- Exportable to standard CSV, JSON, and PDF audit compliance formats.
