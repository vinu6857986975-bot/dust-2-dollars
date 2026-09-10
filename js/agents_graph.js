/**
 * Construct-AI — Multi-Agent Orchestrator Pipeline Graph Visualizer
 * Renders the 9 LangGraph agent nodes, transitions, animated data paths, and interactive inspection.
 */

class AgentsGraphVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.agents = [
      { id: "intent", name: "Intent Agent", icon: "🎯", role: "Request & Task Classifier", tool: "intent_parser" },
      { id: "vision", name: "Vision Agent", icon: "👁️", role: "Spatial Blueprint Detection", tool: "YOLO/Spatial Extractor" },
      { id: "estimation", name: "Estimation Agent", icon: "📐", role: "IS 456 Deterministic Math", tool: "calculations/concrete.py" },
      { id: "material", name: "Material Agent", icon: "📦", role: "BOM Categorization & Units", tool: "bom_normalizer" },
      { id: "cost", name: "Cost Agent", icon: "💰", role: "material_prices DB Lookup", tool: "price_db_query" },
      { id: "supplier", name: "Supplier Agent", icon: "🚚", role: "Multi-Criteria Ranking", tool: "scoring_function" },
      { id: "planning", name: "Planning Agent", icon: "📅", role: "3-Phase Procurement Plan", tool: "gantt_scheduler" },
      { id: "delivery", name: "Delivery Agent", icon: "🚛", role: "Consignment Batching", tool: "truck_batcher" },
      { id: "verification", name: "Verification Agent", icon: "🛡️", role: "5-Point Sanity & Replan Gate", tool: "bounds_checker" }
    ];
    this.nodeStates = {};
    this.init();
  }

  init() {
    if (!this.container) return;
    this.container.innerHTML = "";

    this.agents.forEach((ag, idx) => {
      this.nodeStates[ag.id] = "idle";

      const node = document.createElement("div");
      node.className = "agent-node idle";
      node.id = `agent-node-${ag.id}`;
      node.onclick = () => this.inspectAgent(ag.id);

      node.innerHTML = `
        <div class="agent-node-icon">${ag.icon}</div>
        <div class="agent-node-name">${ag.name}</div>
        <div class="agent-node-role">${ag.role}</div>
        <div class="agent-node-badge" id="badge-${ag.id}" style="font-size:0.68rem; color:var(--text-muted); margin-top:4px;">IDLE</div>
      `;
      this.container.appendChild(node);
    });
  }

  setAgentState(agentId, state, detail = "") {
    this.nodeStates[agentId] = state;
    const node = document.getElementById(`agent-node-${agentId}`);
    const badge = document.getElementById(`badge-${agentId}`);
    if (!node) return;

    node.classList.remove("idle", "running", "done", "replanning");
    node.classList.add(state);

    if (badge) {
      if (state === "running") {
        badge.textContent = "RUNNING...";
        badge.style.color = "var(--cyan-400)";
      } else if (state === "done") {
        badge.textContent = "✓ VERIFIED";
        badge.style.color = "var(--emerald-400)";
      } else if (state === "replanning") {
        badge.textContent = "⚠️ REPLANNING";
        badge.style.color = "var(--amber-400)";
      } else {
        badge.textContent = "IDLE";
        badge.style.color = "var(--text-muted)";
      }
    }
  }

  resetAll() {
    this.agents.forEach(ag => {
      this.setAgentState(ag.id, "idle");
    });
  }

  inspectAgent(agentId) {
    const ag = this.agents.find(a => a.id === agentId);
    if (!ag) return;

    const modal = document.getElementById("agentInspectModal");
    const title = document.getElementById("inspectModalTitle");
    const body = document.getElementById("inspectModalBody");
    if (!modal) return;

    title.innerHTML = `${ag.icon} ${ag.name} — Architecture & Contract`;
    
    // Get live state or default description
    const lastResult = window.ConstructApp ? window.ConstructApp.currentAnalysis : null;
    let liveOutput = "Awaiting execution...";
    if (lastResult && lastResult.outputs && lastResult.outputs[ag.id]) {
      liveOutput = JSON.stringify(lastResult.outputs[ag.id], null, 2);
    }

    body.innerHTML = `
      <div style="margin-bottom: 1.25rem;">
        <span class="section-tag">${ag.role}</span>
        <h4 style="color:var(--text-primary); margin-top:0.5rem; font-size:1.1rem;">Contract & Responsibilities</h4>
        <p style="color:var(--text-secondary); font-size:0.92rem; margin-top:0.35rem;">
          Specialized agent running within the LangGraph state machine. Adheres to Rule 2.1: <em>The LLM never computes quantities or costs directly.</em>
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.25rem;">
        <div style="background:rgba(255,255,255,0.03); padding:0.85rem; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">TOOL INVOCATION</div>
          <div style="color:var(--amber-400); font-family:var(--font-mono); font-size:0.85rem; margin-top:4px;">${ag.tool}</div>
        </div>
        <div style="background:rgba(255,255,255,0.03); padding:0.85rem; border-radius:8px; border:1px solid var(--border-subtle);">
          <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">CURRENT LIFECYCLE STATE</div>
          <div style="color:var(--cyan-400); font-weight:700; font-size:0.85rem; margin-top:4px; text-transform:uppercase;">${this.nodeStates[ag.id] || "IDLE"}</div>
        </div>
      </div>

      <div>
        <div style="font-size:0.8rem; font-weight:700; color:var(--text-muted); text-transform:uppercase; margin-bottom:0.5rem;">Live Agent Output Payload (JSON)</div>
        <pre style="background:#060913; border:1px solid var(--border-subtle); padding:1rem; border-radius:8px; font-family:var(--font-mono); font-size:0.82rem; color:#38bdf8; max-height:220px; overflow-y:auto;">${liveOutput}</pre>
      </div>
    `;

    modal.classList.add("active");
  }
}

window.AgentsGraphVisualizer = AgentsGraphVisualizer;
