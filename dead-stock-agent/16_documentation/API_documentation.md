# API Documentation
- `GET /api/products`: Retrieve all products with inventory status.
- `POST /api/decision/analyze`: Trigger 4-agent cognitive evaluation.
- `POST /api/decision/{id}/approve`: Commit human approval to audit ledger.
- `POST /api/decision/{id}/reject`: Flag recommendation as rejected with feedback.
- `GET /api/dashboard`: Summary aggregates of locked capital, dead inventory counts, and top at-risk SKUs.
- `GET /api/architecture/files`: Retrieve interactive 18-module project repository structure.
