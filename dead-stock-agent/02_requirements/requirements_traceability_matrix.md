# Requirements Traceability Matrix (RTM)

| Req ID | Description | Component | Test Case | Status |
|---|---|---|---|---|
| FR-01 | Ingest product and inventory data | Backend API / SQLite | `test_api.py::test_create_product` | Complete |
| FR-02 | Calculate stock age and holding cost | Stock Agent | `test_stock_agent.py::test_aging` | Complete |
| FR-03 | Enforce supplier return constraints | Strategy Agent / Rules | `test_rules.py::test_supplier_window` | Complete |
| FR-04 | Generate 8 candidate actions | Strategy Agent | `test_strategy_agent.py::test_actions` | Complete |
| FR-05 | Rank feasible actions by score | Decision Engine | `test_decision_engine.py::test_scoring`| Complete |
| FR-06 | Human-in-the-loop approval | Backend / Frontend | `test_user_workflow.py::test_approval`| Complete |
| FR-07 | Neutralize prompt injections | Red Team Guardrails | `test_red_team.py::test_injection` | Complete |
