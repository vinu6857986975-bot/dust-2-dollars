# -*- coding: utf-8 -*-
"""
Generate all remaining diagrams, markdown specifications, tests, and data files.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def write(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print("Writing extended architecture diagrams, tests, and data...")

# ── 03_FLOWCHARTS ───────────────────────────────────────────
write("03_flowcharts/agent_workflow.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 400" width="100%" height="100%">
  <rect width="100%" height="100%" fill="#080B10"/>
  <text x="375" y="35" fill="#38BDF8" font-size="18" font-weight="bold" font-family="system-ui" text-anchor="middle">Multi-Agent Workflow Sequence</text>
  
  <g transform="translate(40, 80)">
    <rect width="140" height="80" rx="8" fill="#1E293B" stroke="#EF4444" stroke-width="2"/>
    <text x="70" y="30" fill="#F87171" font-size="13" font-weight="bold" text-anchor="middle">Stock Agent</text>
    <text x="70" y="52" fill="#94A3B8" font-size="10" text-anchor="middle">Computes Age &amp; Velocity</text>
  </g>
  <path d="M180,120 L210,120" stroke="#6366F1" stroke-width="3"/>
  
  <g transform="translate(210, 80)">
    <rect width="140" height="80" rx="8" fill="#1E293B" stroke="#F59E0B" stroke-width="2"/>
    <text x="70" y="30" fill="#FCD34D" font-size="13" font-weight="bold" text-anchor="middle">Product Agent</text>
    <text x="70" y="52" fill="#94A3B8" font-size="10" text-anchor="middle">Margin &amp; Elasticity</text>
  </g>
  <path d="M350,120 L380,120" stroke="#6366F1" stroke-width="3"/>
  
  <g transform="translate(380, 80)">
    <rect width="140" height="80" rx="8" fill="#1E293B" stroke="#6366F1" stroke-width="2"/>
    <text x="70" y="30" fill="#A5B4FC" font-size="13" font-weight="bold" text-anchor="middle">Strategy Agent</text>
    <text x="70" y="52" fill="#94A3B8" font-size="10" text-anchor="middle">Generates 8 Tactics</text>
  </g>
  <path d="M520,120 L550,120" stroke="#6366F1" stroke-width="3"/>
  
  <g transform="translate(550, 80)">
    <rect width="160" height="80" rx="8" fill="#1E293B" stroke="#10B981" stroke-width="2"/>
    <text x="80" y="30" fill="#34D399" font-size="13" font-weight="bold" text-anchor="middle">Decision Engine</text>
    <text x="80" y="52" fill="#94A3B8" font-size="10" text-anchor="middle">Hard Filters + LLM Explain</text>
  </g>
  
  <path d="M630,160 L630,230 L375,230 L375,260" stroke="#10B981" stroke-width="2" fill="none" stroke-dasharray="4"/>
  <g transform="translate(275, 260)">
    <rect width="200" height="60" rx="8" fill="#047857"/>
    <text x="100" y="28" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">Validated Recommendation</text>
    <text x="100" y="46" fill="#D1FAE5" font-size="11" text-anchor="middle">Presented to User for Sign-off</text>
  </g>
</svg>
""")

write("03_flowcharts/decision_flowchart.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 450" width="100%" height="100%">
  <rect width="100%" height="100%" fill="#080B10"/>
  <text x="350" y="35" fill="#A5B4FC" font-size="18" font-weight="bold" font-family="system-ui" text-anchor="middle">Decision Logic &amp; Hard Constraint Tree</text>
  
  <g transform="translate(250, 60)">
    <rect width="200" height="40" rx="6" fill="#1E293B" stroke="#6366F1"/>
    <text x="100" y="24" fill="#E2E8F0" font-size="12" text-anchor="middle">Candidate: Return to Supplier?</text>
  </g>
  
  <path d="M350,100 L350,140" stroke="#6366F1" stroke-width="2"/>
  
  <g transform="translate(230, 140)">
    <polygon points="120,0 240,40 120,80 0,40" fill="#312E81" stroke="#818CF8"/>
    <text x="120" y="36" fill="#fff" font-size="11" text-anchor="middle">Stock Age &lt;=</text>
    <text x="120" y="50" fill="#fff" font-size="11" text-anchor="middle">Return Window?</text>
  </g>
  
  <path d="M230,180 L140,180 L140,240" stroke="#EF4444" stroke-width="2"/>
  <text x="175" y="172" fill="#F87171" font-size="11">NO</text>
  <g transform="translate(60, 240)">
    <rect width="160" height="50" rx="6" fill="#450A0A" stroke="#EF4444"/>
    <text x="80" y="24" fill="#FCA5A5" font-size="11" font-weight="bold" text-anchor="middle">DROP ACTION</text>
    <text x="80" y="38" fill="#FCA5A5" font-size="9" text-anchor="middle">Violates Contract SLA</text>
  </g>
  
  <path d="M470,180 L560,180 L560,240" stroke="#10B981" stroke-width="2"/>
  <text x="505" y="172" fill="#34D399" font-size="11">YES</text>
  <g transform="translate(480, 240)">
    <rect width="160" height="50" rx="6" fill="#064E3B" stroke="#10B981"/>
    <text x="80" y="24" fill="#6EE7B7" font-size="11" font-weight="bold" text-anchor="middle">FEASIBLE ACTION</text>
    <text x="80" y="38" fill="#6EE7B7" font-size="9" text-anchor="middle">Assigned Feasibility Score</text>
  </g>
</svg>
""")

# ── 04_ARCHITECTURE ─────────────────────────────────────────
write("04_architecture/system_architecture.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <rect width="100%" height="100%" fill="#0A0D14"/>
  <text x="400" y="35" fill="#38BDF8" font-size="20" font-weight="bold" font-family="system-ui" text-anchor="middle">AnyPortal System Architecture</text>
  
  <!-- Client Tier -->
  <rect x="50" y="70" width="700" height="70" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
  <text x="70" y="95" fill="#38BDF8" font-size="12" font-weight="bold">PRESENTATION LAYER (10_FRONTEND)</text>
  <text x="70" y="120" fill="#94A3B8" font-size="12">Interactive Cyber UI • Canvas Particle Visualizer • What-If Sandbox • Red Team Lab • Decision Studio</text>
  
  <!-- Backend API -->
  <rect x="50" y="170" width="700" height="70" rx="10" fill="#1E293B" stroke="#6366F1" stroke-width="2"/>
  <text x="70" y="195" fill="#818CF8" font-size="12" font-weight="bold">APPLICATION &amp; ORCHESTRATION LAYER (06_BACKEND)</text>
  <text x="70" y="220" fill="#94A3B8" font-size="12">FastAPI / Python Stdlib REST Server • Agent Pipeline Orchestrator • SQLite WAL Database Service</text>
  
  <!-- Intelligence & Data -->
  <rect x="50" y="270" width="340" height="180" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="2"/>
  <text x="70" y="295" fill="#34D399" font-size="12" font-weight="bold">COGNITIVE AI &amp; NLP LAYER</text>
  <text x="70" y="325" fill="#E2E8F0" font-size="11">• Stock Aging Analyzer (07_AI_NLP)</text>
  <text x="70" y="350" fill="#E2E8F0" font-size="11">• Category Elasticity Agent</text>
  <text x="70" y="375" fill="#E2E8F0" font-size="11">• Deterministic Scoring Engine</text>
  <text x="70" y="400" fill="#E2E8F0" font-size="11">• OpenAI GPT-4o-mini Context Rationale</text>
  <text x="70" y="425" fill="#E2E8F0" font-size="11">• Built-in Offline Fallback Generator</text>
  
  <rect x="410" y="270" width="340" height="180" rx="10" fill="#1E293B" stroke="#F59E0B" stroke-width="2"/>
  <text x="430" y="295" fill="#FCD34D" font-size="12" font-weight="bold">POLICY GRAPH &amp; GOVERNANCE LAYER</text>
  <text x="430" y="325" fill="#E2E8F0" font-size="11">• Knowledge Graph (08_KNOWLEDGE_GRAPH)</text>
  <text x="430" y="350" fill="#E2E8F0" font-size="11">• Hard Constraint Filter (Supplier SLA)</text>
  <text x="430" y="375" fill="#E2E8F0" font-size="11">• Red Team Injection Shield (14_RED_TEAM)</text>
  <text x="430" y="400" fill="#E2E8F0" font-size="11">• Immutable SQLite Audit Log (05_DATABASE)</text>
  <text x="430" y="425" fill="#E2E8F0" font-size="11">• Human-in-the-Loop Approval Gateway</text>
</svg>
""")

# ── 05_DATABASE ─────────────────────────────────────────────
write("05_database/sample_data.json", json.dumps({
    "products": [
        {"id": 1, "sku": "JKT-WTR-001", "name": "Winter Parka Nordic Down", "category": "Apparel", "brand": "Nordic Weavers", "cost_price": 1500.0, "selling_price": 2499.0, "supplier_id": 1},
        {"id": 2, "sku": "SW-CHR-002", "name": "Smart Fitness Watch Gen 2", "category": "Electronics", "brand": "PulseTech", "cost_price": 2200.0, "selling_price": 4499.0, "supplier_id": 2},
        {"id": 3, "sku": "BOO-LTH-003", "name": "Leather Ankle Chelsea Boots", "category": "Footwear", "brand": "UrbanStride", "cost_price": 1800.0, "selling_price": 3299.0, "supplier_id": 3}
    ],
    "inventory": [
        {"id": 1, "product_id": 1, "quantity": 42, "location": "Warehouse North", "stock_since": "2026-04-15", "age_days": 147},
        {"id": 2, "product_id": 2, "quantity": 28, "location": "Central Hub", "stock_since": "2026-08-10", "age_days": 30},
        {"id": 3, "product_id": 3, "quantity": 65, "location": "Warehouse South", "stock_since": "2026-03-01", "age_days": 192}
    ],
    "suppliers": [
        {"id": 1, "name": "Nordic Weavers Ltd", "return_allowed": 1, "return_window_days": 30, "restocking_fee_pct": 10.0},
        {"id": 2, "name": "PulseTech Global", "return_allowed": 1, "return_window_days": 45, "restocking_fee_pct": 5.0},
        {"id": 3, "name": "UrbanStride Footwear", "return_allowed": 0, "return_window_days": 0, "restocking_fee_pct": 0.0}
    ]
}, indent=2))

# ── 07_AI_NLP SCHEMAS ───────────────────────────────────────
write("07_ai_nlp/schemas/decision_output.json", json.dumps({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "DecisionOutput",
    "type": "object",
    "required": ["recommended_action", "confidence", "reasoning", "candidate_actions"],
    "properties": {
        "recommended_action": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
        "reasoning": {"type": "string"},
        "expected_capital_recovery": {"type": "number"},
        "candidate_actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "score": {"type": "number"},
                    "feasible": {"type": "boolean"},
                    "reason": {"type": "string"}
                }
            }
        }
    }
}, indent=2))

# ── 08_KNOWLEDGE_BASE ───────────────────────────────────────
write("08_knowledge_graph_rag/knowledge_base/supplier_policies/nordic_weavers.md", """# Supplier Policy: Nordic Weavers Ltd
- **Return Eligibility:** Returns accepted within 30 days of shipment receipt.
- **Restocking Fee:** 10% on original procurement value.
- **Condition Requirements:** Tags intact, original protective packaging.
- **Past Window Penalty:** Any return attempted past 30 days is rejected outright.
""")

write("08_knowledge_graph_rag/knowledge_base/business_rules/margin_guardrails.md", """# Enterprise Business Rules: Margin Guardrails
- **Rule BR-01:** Minimum Gross Margin Floor: No promotional discount may result in an item gross margin below 10% without executive sign-off.
- **Rule BR-02:** Clearance Maximum: Clearance liquidation discounts are capped at 50% for standard categories.
""")

# ── DATA DIRECTORY ──────────────────────────────────────────
write("data/products.json", json.dumps([
    {"sku": "JKT-WTR-001", "name": "Winter Down Parka", "category": "Apparel", "cost": 1500, "price": 2499, "supplier": "Nordic Weavers Ltd"},
    {"sku": "SW-CHR-002", "name": "Smart Fitness Watch Gen 2", "category": "Electronics", "cost": 2200, "price": 4499, "supplier": "PulseTech Global"},
    {"sku": "BOO-LTH-003", "name": "Chelsea Leather Boots", "category": "Footwear", "cost": 1800, "price": 3299, "supplier": "UrbanStride Footwear"}
], indent=2))

# ── ROOT SPECS ──────────────────────────────────────────────
write("requirements.txt", """# AnyPortal Business Dead-Stock Decision Agent
# Standard library execution requires zero pip installs!
# Optional packages for development, FastAPI, or extended tests:
# fastapi>=0.100.0
# uvicorn>=0.23.0
# requests>=2.31.0
""")

write("package.json", json.dumps({
    "name": "anyportal-dead-stock-agent",
    "version": "2.4.0",
    "description": "AnyPortal Business Dead-Stock Decision Agent - Autonomous Multi-Agent AI Platform",
    "scripts": {
        "start": "python server.py",
        "test": "python -m unittest discover -s 13_testing/unit"
    },
    "keywords": ["agentic-ai", "dead-stock", "inventory-management", "retail-tech"],
    "author": "AnyPortal AI Team",
    "license": "MIT"
}, indent=2))

write(".env.example", """# AnyPortal Environment Configuration
PORT=8001
HOST=0.0.0.0
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DEBUG=true
DB_PATH=dust2dollar.db
""")

print("Extended files successfully written.")

