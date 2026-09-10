"""
Construct-AI Orchestrator Agent
LangGraph State Machine Coordinator with Bounded Replanning
"""
import json
from datetime import datetime
from agents.pipeline import ConstructAgentsPipeline

class OrchestratorAgent:
    def __init__(self):
        self.pipeline = ConstructAgentsPipeline()

    def run(self, project_payload: dict, simulate_violation=None):
        return self.pipeline.run_orchestrator(project_payload, simulate_violation=simulate_violation)

orchestrator = OrchestratorAgent()
