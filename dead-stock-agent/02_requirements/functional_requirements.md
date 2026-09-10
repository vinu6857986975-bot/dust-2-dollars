# Functional Requirements Specification

| Requirement ID | Module | Description | Acceptance Criteria |
|---|---|---|---|
| FR-STOCK-01 | Stock Agent | Compute stock age from receipt timestamp | Age accurately calculated against system clock |
| FR-STOCK-02 | Stock Agent | Compute total capital at risk = Qty * Cost | Value matches accounting product |
| FR-PROD-01 | Product Agent | Calculate gross profit margin % | Margin = ((Price - Cost)/Price) * 100 |
| FR-PROD-02 | Product Agent | Estimate demand elasticity by category | Mapped to category elasticity coefficient |
| FR-STRAT-01 | Strategy Agent | Filter candidates against hard policy rules | Disallowed actions excluded from final ranking |
| FR-DEC-01 | Decision Engine | Rank candidates by composite score | Highest score selected as primary action |
| FR-DEC-02 | Decision Engine | Generate human-readable justification | Summary contains rationale, financial impact, and risks |
| FR-AUDIT-01 | Governance | Record user approval status | Database stores status: pending, approved, or rejected |
