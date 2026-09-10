# Security Requirements & Threat Model
1. Data Invariant: No prompt text may directly alter product prices or delete inventory.
2. Injection Prevention: All user strings parameterized before LLM prompt assembly.
3. Least Privilege: Local SQLite opened with application-level role restrictions.
