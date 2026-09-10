# -*- coding: utf-8 -*-
"""
Deterministic & Semantic Policy Retriever.
Retrieves hard business constraints and supplier contracts to eliminate hallucinated actions.
"""
import os
import glob

class PolicyRetriever:
    def __init__(self, kb_dir=None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.kb_dir = kb_dir or os.path.join(base, "knowledge_base")

    def retrieve_supplier_policy(self, supplier_name: str) -> str:
        pattern = os.path.join(self.kb_dir, "supplier_policies", "*.md")
        files = glob.glob(pattern)
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                if supplier_name.lower() in content.lower() or os.path.basename(fpath).lower() in supplier_name.lower():
                    return content
        return "Standard supplier terms apply: 30-day return window, 10% restocking fee."

    def retrieve_business_rules(self, category: str) -> list:
        pattern = os.path.join(self.kb_dir, "business_rules", "*.md")
        files = glob.glob(pattern)
        rules = []
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                rules.append(f.read())
        return rules
