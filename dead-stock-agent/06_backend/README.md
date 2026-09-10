# 06_BACKEND — DUST 2 DOLLAR API Service

## Architectural Overview
The `06_backend` module provides an enterprise-grade, asynchronous REST API service built with **FastAPI**. It connects client applications to the 4-agent cognitive pipeline, business rule constraint engine, and persistent SQLite/PostgreSQL storage.

```
06_backend/
├── app/
│   ├── main.py            # Application factory, middleware & router mounts
│   ├── api/               # Modular REST endpoints (products, inventory, decisions, etc.)
│   ├── agents/            # Multi-agent cognitive decision engine
│   ├── database/          # Connection manager and query helpers
│   ├── models/            # Domain models and database entities
│   └── schemas/           # Pydantic schemas for request/response validation
├── Dockerfile             # Container definition for containerized backend
├── requirements.txt       # Production dependencies
└── README.md
```

## Running the Backend
### Direct Run (FastAPI):
```bash
uvicorn app.main:app --reload --port 8000
```

### Zero-Dependency Portable Run:
The root launcher `server.py` in `dead-stock-agent/` also provides an instant zero-dependency HTTP server implementing these exact endpoints natively via Python 3 standard library.
