# -*- coding: utf-8 -*-
"""
Knowledge Graph Builder for Retail Dead-Stock Constraints.
Builds an in-memory graph connecting Products -> Categories -> Suppliers -> Return Policies.
"""
import json
import os

class KnowledgeGraphBuilder:
    def __init__(self, entities_path=None, relations_path=None):
        base = os.path.dirname(os.path.abspath(__file__))
        self.entities_path = entities_path or os.path.join(base, "knowledge_graph", "entities.json")
        self.relations_path = relations_path or os.path.join(base, "knowledge_graph", "relationships.json")
        self.nodes = {}
        self.edges = []
        self.build()

    def build(self):
        if os.path.exists(self.entities_path):
            with open(self.entities_path, "r", encoding="utf-8") as f:
                raw_nodes = json.load(f)
                for node in raw_nodes:
                    self.nodes[node["id"]] = node

        if os.path.exists(self.relations_path):
            with open(self.relations_path, "r", encoding="utf-8") as f:
                self.edges = json.load(f)

    def query_supplier_policy(self, product_id_or_sku: str):
        """Finds supplier and policy nodes linked to a product."""
        results = {"product": None, "supplier": None, "policy": None, "constraints": []}
        for edge in self.edges:
            if edge["source"] == product_id_or_sku and edge["relation"] == "SUPPLIED_BY":
                sup_id = edge["target"]
                results["supplier"] = self.nodes.get(sup_id)
                # Find policy
                for pol_edge in self.edges:
                    if pol_edge["source"] == sup_id and pol_edge["relation"] == "HAS_POLICY":
                        results["policy"] = self.nodes.get(pol_edge["target"])
                        results["policy_meta"] = pol_edge.get("properties", {})
        return results

if __name__ == "__main__":
    kg = KnowledgeGraphBuilder()
    print("Nodes loaded:", len(kg.nodes))
    print("Edges loaded:", len(kg.edges))
    print("Query PROD-001 policy:", kg.query_supplier_policy("PROD-001"))
