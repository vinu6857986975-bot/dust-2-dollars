# LLM Security & Guardrails

1. **Non-Executable Policy Barrier:** The LLM NEVER executes financial trades, database drops, or vendor orders directly.
2. **Prompt Injection Containment:** All user inputs are sanitized and parameterized before entering prompt templates.
3. **Deterministic Constraint Override:** If an LLM suggests an illegal action (e.g. returning an item past its return window), the application-level constraint engine overrides the decision with an error code.
