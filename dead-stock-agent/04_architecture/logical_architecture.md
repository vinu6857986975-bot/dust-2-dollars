# Logical Architecture Specification

1. **Presentation Layer (10_frontend):**
   - Single Page Application (SPA).
   - Reactive UI State Controller (`app.js`).
   - Canvas-based telemetry and interactive animations.

2. **Application & API Layer (06_backend):**
   - RESTful endpoint routing (`server.py`).
   - JSON request schema serialization and deserialization.
   - Cross-Origin Resource Sharing (CORS) security headers.

3. **Cognitive & Agentic Layer (07_ai_nlp, 08_knowledge_graph_rag):**
   - Orchestrator coordinator pattern.
   - Heuristic decision tree with fallback redundancy.
   - LLM integration layer with strict JSON schema outputs.

4. **Persistence Layer (05_database):**
   - SQLite 3 with Write-Ahead Logging (WAL).
   - Foreign-key enforced transactional integrity.
