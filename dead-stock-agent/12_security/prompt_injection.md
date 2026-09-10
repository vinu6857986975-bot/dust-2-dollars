# Prompt Injection Defense Strategy
- Dual-barrier architecture: LLM outputs are treated as UNTRUSTED proposals.
- Proposals pass through deterministic Python validators before rendering or execution.
- If an LLM proposes a 90% discount, the validator clamps or rejects it against `rules.margin_floor`.
