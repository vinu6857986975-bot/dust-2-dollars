# Software Requirements Specification (SRS)
## Standard: IEEE 830-1998 Compatible

### 1. Functional Requirements (FR)
- **FR-01 (Data Ingestion):** The system SHALL accept inventory inputs containing SKU, name, category, quantity, cost price, retail price, stock received date, and supplier ID.
- **FR-02 (Aging Computation):** The system SHALL compute holding days: Age = CurrentDate - StockSinceDate, classifying items as Active (<60d), Slow (60-90d), At-Risk (90-120d), or Dead Stock (>120d).
- **FR-03 (Supplier Verification):** The system SHALL query supplier contracts to verify if return_allowed == True and Age <= return_window_days.
- **FR-04 (Candidate Generation):** The Strategy Agent SHALL generate candidate recovery actions from an approved taxonomy of 8 strategies.
- **FR-05 (Action Scoring):** The system SHALL score candidate actions using the Composite Capital Recovery Scoring formula.
- **FR-06 (Constraint Pruning):** The Constraint Engine SHALL prune any candidate action violating minimum margin or return window limits.
- **FR-07 (LLM Explanation):** The Decision Engine SHALL synthesize a natural-language executive summary detailing the rationale, risks, and recovery projections.
- **FR-08 (Human Approval Workflow):** The system SHALL provide endpoints to approve, reject, or modify recommendations.
- **FR-09 (Audit Persistence):** All decisions, timestamps, agent traces, and operator choices SHALL persist into an SQLite database.
- **FR-10 (What-If Simulation):** The system SHALL provide a live parametric sandbox recalculating scores instantaneously.
- **FR-11 (Red Team Defenses):** The system SHALL reject adversarial prompt injection strings targeting discount floors or rule bypasses.
- **FR-12 (Data Export):** The system SHALL export inventory and decision ledgers in JSON and CSV formats.

### 2. Non-Functional Requirements (NFR)
- **NFR-01 (Performance):** Average pipeline latency SHALL be < 2,500ms for LLM mode and < 250ms for offline fallback mode.
- **NFR-02 (Availability):** The application SHALL run independently on standard hardware with zero internet-dependency in fallback mode.
- **NFR-03 (Security):** System SHALL prevent prompt leakage, SQL injection, and unauthorized parameter overrides.
- **NFR-04 (Portability):** System SHALL run on Windows, macOS, and Linux without native binary compilation.
