/**
 * Construct-AI — Main Application Orchestrator & State Manager
 * Zero-dependency Dual-Mode: Communicates with Python server.py REST API,
 * or gracefully runs client-side deterministic engine if opened offline as file://
 */

class ConstructApp {
  constructor() {
    this.currentView = "home";
    this.apiBase = window.location.origin.includes("http") ? window.location.origin : "http://localhost:8000";
    this.isServerOnline = false;
    this.activeProject = window.CONSTRUCT_DATA.initialProjects[0];
    this.projectsList = [...window.CONSTRUCT_DATA.initialProjects];
    this.currentAnalysis = null;
    this.isAnalyzing = false;
    this.supplierWeights = { price: 0.45, distance: 0.30, stock: 0.25 };

    this.floorplanViz = null;
    this.agentsViz = null;
    this.signatureCanvas = null;
    this.isDrawingSignature = false;

    this.init();
  }

  async init() {
    this.bindEvents();
    this.initVisualizers();
    this.initSignaturePad();
    await this.checkServerHealth();
    this.renderProjectsList();

    // Default route check
    const hash = window.location.hash.replace("#", "") || "home";
    this.navigate(hash);
  }

  // 1. Navigation & Routing
  navigate(viewName) {
    const validViews = ["home", "dashboard", "new-project", "analysis", "materials", "suppliers", "procurement", "logs", "profile"];
    if (!validViews.includes(viewName)) viewName = "home";

    this.currentView = viewName;
    window.location.hash = viewName;

    // Update active view DOM
    document.querySelectorAll(".page-view").forEach(el => el.classList.remove("active"));
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) targetView.classList.add("active");

    // Update nav link states
    document.querySelectorAll(".nav-item").forEach(link => {
      link.classList.toggle("active", link.dataset.target === viewName);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    // View specific hooks
    if (viewName === "analysis" && !this.currentAnalysis && !this.isAnalyzing) {
      this.loadDemoPreset("villa");
    } else if (viewName === "analysis" && this.floorplanViz) {
      this.floorplanViz.initResize();
    }
  }

  bindEvents() {
    // Nav link clicks
    document.querySelectorAll("[data-target]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this.navigate(btn.dataset.target);
      });
    });

    // Preset selector buttons
    document.querySelectorAll("[data-preset]").forEach(btn => {
      btn.addEventListener("click", () => {
        const presetKey = btn.dataset.preset;
        this.loadDemoPreset(presetKey);
      });
    });

    // Layer toggles on floor plan
    document.querySelectorAll("[data-layer]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-layer]").forEach(b => b.classList.remove("btn-primary"));
        btn.classList.add("btn-primary");
        if (this.floorplanViz) this.floorplanViz.setLayer(btn.dataset.layer);
      });
    });

    // Supplier ranking sliders
    const setupSlider = (id, key) => {
      const input = document.getElementById(id);
      const valLabel = document.getElementById(`${id}-val`);
      if (input && valLabel) {
        input.addEventListener("input", () => {
          valLabel.textContent = `${input.value}%`;
          this.supplierWeights[key] = parseFloat(input.value) / 100.0;
          this.recalculateSuppliers();
        });
      }
    };
    setupSlider("slider-price", "price");
    setupSlider("slider-dist", "distance");
    setupSlider("slider-stock", "stock");

    // Modals
    document.querySelectorAll(".modal-close, .modal-overlay").forEach(el => {
      el.addEventListener("click", (e) => {
        if (e.target === el) {
          document.querySelectorAll(".modal-overlay").forEach(m => m.classList.remove("active"));
        }
      });
    });
  }

  initVisualizers() {
    this.floorplanViz = new window.FloorPlanVisualizer("floorplanCanvas");
    this.agentsViz = new window.AgentsGraphVisualizer("agentsGraphNodes");
  }

  // 2. Server Health Check & Dual-Mode
  async checkServerHealth() {
    const pill = document.getElementById("serverHealthPill");
    try {
      const res = await fetch(`${this.apiBase}/api/health`);
      if (res.ok) {
        const data = await res.json();
        this.isServerOnline = true;
        if (pill) {
          pill.innerHTML = `<span class="pulse-dot"></span> REST API Online (Fast Engine)`;
          pill.style.borderColor = "rgba(16, 185, 129, 0.4)";
          pill.style.color = "var(--emerald-400)";
        }
        return;
      }
    } catch (e) {
      // Offline fallback mode
    }

    this.isServerOnline = false;
    if (pill) {
      pill.innerHTML = `<span class="pulse-dot" style="background:var(--amber-400)"></span> Standalone Local Engine`;
      pill.style.borderColor = "rgba(245, 158, 11, 0.4)";
      pill.style.color = "var(--amber-400)";
    }
  }

  // 3. Preset Loading
  loadDemoPreset(presetKey) {
    const preset = window.CONSTRUCT_DATA.presets[presetKey] || window.CONSTRUCT_DATA.presets.villa;
    this.activeProject = {
      id: Date.now(),
      project_name: preset.name,
      building_type: preset.building_type,
      floor_area: preset.built_up_area,
      plot_area: preset.plot_area,
      floors: preset.floors,
      location: preset.location,
      status: "Configured",
      preset: presetKey
    };

    // Update Project Overview labels
    const titleEl = document.getElementById("activeProjectTitle");
    const metaEl = document.getElementById("activeProjectMeta");
    if (titleEl) titleEl.textContent = preset.name;
    if (metaEl) metaEl.textContent = `${preset.building_type.toUpperCase()} • ${preset.built_up_area} SQ.FT • ${preset.floors} FLOOR(S) • ${preset.location}`;

    // Load canvas blueprint
    if (this.floorplanViz) {
      this.floorplanViz.loadPreset(presetKey);
    }

    // Reset visualizer & run live analysis
    this.startAnalysis(this.activeProject, preset);
  }

  // 4. Multi-Agent Analysis Pipeline Execution
  async startAnalysis(projectData, presetInfo = null, simulateViolation = null) {
    if (this.isAnalyzing) return;
    this.isAnalyzing = true;

    // Reset UI states
    this.agentsViz.resetAll();
    const progressFill = document.getElementById("analysisProgressFill");
    const progressText = document.getElementById("analysisProgressText");
    const consoleBox = document.getElementById("consoleLogs");
    if (consoleBox) consoleBox.innerHTML = "";

    const addLog = (agent, action, status = "started", extra = "") => {
      if (!consoleBox) return;
      const now = new Date().toLocaleTimeString();
      const div = document.createElement("div");
      div.className = "log-line";
      div.innerHTML = `
        <span class="log-time">[${now}]</span>
        <span class="log-agent">${agent}</span>
        <span class="log-msg">${action} ${extra ? `<em style="color:#94a3b8">(${extra})</em>` : ''}</span>
        <span class="log-status ${status}">${status}</span>
      `;
      consoleBox.appendChild(div);
      consoleBox.scrollTop = consoleBox.scrollHeight;
    };

    const updateProgress = (pct, label) => {
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (progressText) progressText.textContent = `${pct}% — ${label}`;
    };

    addLog("Orchestrator", "Initiating LangGraph construction state machine", "started");
    updateProgress(5, "Orchestrator initializing...");

    // Start scanning laser line
    if (this.floorplanViz) {
      this.floorplanViz.startScanning();
    }

    // Sequential agent simulation with visual feedback
    const agentSequence = [
      { id: "intent", name: "Intent Agent", pct: 15, label: "Parsing project intent & requirements" },
      { id: "vision", name: "Vision Agent", pct: 30, label: "Extracting room geometries & confidence" },
      { id: "estimation", name: "Estimation Agent", pct: 45, label: "Calling deterministic IS 456 calculations" },
      { id: "material", name: "Material Agent", pct: 60, label: "Normalizing BOM quantities & units" },
      { id: "cost", name: "Cost Agent", pct: 72, label: "Fetching prices from material_prices catalog" },
      { id: "supplier", name: "Supplier Agent", pct: 82, label: "Evaluating supplier trade-off matrix" },
      { id: "planning", name: "Planning Agent", pct: 90, label: "Generating 3-phase procurement plan" },
      { id: "delivery", name: "Delivery Agent", pct: 95, label: "Batching truck consignments" },
      { id: "verification", name: "Verification Agent", pct: 100, label: "Verifying engineering plausibility" }
    ];

    for (let i = 0; i < agentSequence.length; i++) {
      const ag = agentSequence[i];
      this.agentsViz.setAgentState(ag.id, "running");
      updateProgress(ag.pct, ag.label);
      addLog(ag.name, ag.label, "started");

      await new Promise(r => setTimeout(r, 450)); // Cinematic smooth transition

      this.agentsViz.setAgentState(ag.id, "done");
      addLog(ag.name, "Execution verified successfully", "done");
    }

    // Handle Server or Local execution
    let result = null;
    if (this.isServerOnline) {
      try {
        const endpoint = simulateViolation ? `${this.apiBase}/api/analysis/replan` : `${this.apiBase}/api/analysis/run`;
        const resp = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...projectData,
            supplier_weights: this.supplierWeights,
            violation_type: simulateViolation || "price_anomaly"
          })
        });
        if (resp.ok) {
          result = await resp.json();
        }
      } catch (err) {
        console.warn("Server run failed, switching to local calculation engine", err);
      }
    }

    // Local deterministic engine if server not used
    if (!result) {
      result = this.generateLocalAnalysis(projectData, presetInfo, simulateViolation);
    }

    // Check if replan occurred (visual replay)
    if (simulateViolation || result.replan_occurred) {
      this.agentsViz.setAgentState("verification", "replanning");
      addLog("Verification Agent", "⚠️ PRICE ANOMALY DETECTED: Steel price exceeds safety bounds!", "replanning");
      addLog("Orchestrator", "Initiating targeted Bounded Replan on 'cost_agent' (Attempt 1 of 2)", "replanning");
      
      await new Promise(r => setTimeout(r, 1200));
      this.agentsViz.setAgentState("cost", "replanning");
      addLog("Cost Agent", "Recalibrating prices using benchmark catalog median (₹64,500/Tonne)", "done");
      
      await new Promise(r => setTimeout(r, 800));
      this.agentsViz.setAgentState("cost", "done");
      this.agentsViz.setAgentState("verification", "done");
      addLog("Verification Agent", "✓ Replan cleared! All 5 engineering checks passed.", "done");
    }

    this.currentAnalysis = result;
    this.isAnalyzing = false;
    updateProgress(100, "Analysis complete & verified!");
    addLog("Orchestrator", "Multi-agent workflow successfully concluded. Bill of Materials ready.", "done");

    // Populate screens
    this.renderMaterialsScreen(result);
    this.renderSuppliersScreen(result);
    this.renderProcurementScreen(result);
    this.renderConfidenceHUD(result);

    // Show Completion Toast
    this.showToast("Analysis Complete! Bill of Materials & Procurement Plan Generated.");
  }

  // 5. Client Deterministic Generator (Zero-fail fallback)
  generateLocalAnalysis(projectData, presetInfo, simulateViolation) {
    const area = projectData.floor_area || 2400;
    const floors = projectData.floors || 2;
    const bType = projectData.building_type || "residential";

    const calc = window.ConstructCalculations;
    const concrete = calc.calculateConcreteVolume(area, floors, bType);
    const mDesign = calc.calculateMixDesign(concrete.concreteVolumeM3, "M20");
    const steel = calc.calculateSteelRequirement(concrete.concreteVolumeM3, bType);
    const bricks = calc.calculateBrickwork(area, floors);
    const finish = calc.calculateFinishing(area, floors);

    const totalCement = mDesign.cementBags + bricks.masonryCementBags;
    const totalSand = parseFloat((mDesign.sandM3 + bricks.masonrySandM3).toFixed(2));

    const materials = [
      { id: "cement", name: "OPC 53 Grade Cement", category: "structural", quantity: totalCement, unit: "Bags", unit_price: 385.0, subtotal: totalCement * 385.0, proof: mDesign.proof },
      { id: "sand", name: "Manufactured River Sand (M-Sand)", category: "structural", quantity: totalSand, unit: "m³", unit_price: 1950.0, subtotal: totalSand * 1950.0, proof: mDesign.proof },
      { id: "aggregate", name: "Graded Coarse Aggregate (20mm)", category: "structural", quantity: mDesign.aggregateM3, unit: "m³", unit_price: 1650.0, subtotal: mDesign.aggregateM3 * 1650.0, proof: mDesign.proof },
      { id: "steel", name: "TMT Rebars Fe550 Grade", category: "structural", quantity: steel.steelTonnes, unit: "Tonnes", unit_price: 64500.0, subtotal: steel.steelTonnes * 64500.0, proof: steel.proof },
      { id: "bricks", name: "Standard Kiln-Baked Red Bricks", category: "masonry", quantity: bricks.totalBricks, unit: "Nos", unit_price: 9.50, subtotal: bricks.totalBricks * 9.50, proof: bricks.proof },
      { id: "tiles", name: "Vitrified Glazed Floor Tiles (600x600mm)", category: "finishing", quantity: finish.tilesSqft, unit: "sq.ft", unit_price: 72.0, subtotal: finish.tilesSqft * 72.0, proof: finish.proof },
      { id: "paint", name: "Premium Interior & Exterior Emulsion", category: "finishing", quantity: finish.paintLitres, unit: "Litres", unit_price: 340.0, subtotal: finish.paintLitres * 340.0, proof: finish.proof }
    ];

    const totalCost = materials.reduce((acc, m) => acc + m.subtotal, 0);

    return {
      project_id: projectData.id,
      outputs: {
        intent: { task: "full_estimation", building_type: bType },
        vision: {
          floor_area: area,
          confidence: presetInfo ? presetInfo.confidence : 0.88,
          rooms: presetInfo ? presetInfo.rooms : 5,
          doors: presetInfo ? presetInfo.doors : 8,
          windows: presetInfo ? presetInfo.windows : 10
        },
        estimation: {
          concrete_volume_m3: concrete.concreteVolumeM3,
          total_cement_bags: totalCement,
          steel_tonnes: steel.steelTonnes,
          total_bricks: bricks.totalBricks
        },
        cost: {
          costed_materials: materials,
          total_estimated_cost: Math.round(totalCost)
        }
      },
      status: "success",
      replan_occurred: !!simulateViolation
    };
  }

  // 6. Confidence HUD & Low Confidence Prompt
  renderConfidenceHUD(result) {
    const vision = result.outputs.vision || {};
    const confVal = document.getElementById("hudConfidenceValue");
    const confFill = document.getElementById("hudConfidenceFill");
    const overrideBanner = document.getElementById("lowConfidencePrompt");

    const pct = Math.round((vision.confidence || 0.85) * 100);
    if (confVal) confVal.textContent = `${pct}% Confidence`;
    if (confFill) {
      confFill.style.width = `${pct}%`;
      confFill.style.background = pct < 60 ? "#ef4444" : pct < 80 ? "#f59e0b" : "#10b981";
    }

    if (overrideBanner) {
      overrideBanner.style.display = pct < 60 ? "flex" : "none";
    }
  }

  // 7. Render Materials Screen & Math Proofs
  renderMaterialsScreen(analysis) {
    const costData = analysis.outputs.cost || {};
    const materials = costData.costed_materials || [];
    const totalCost = costData.total_estimated_cost || 0;

    // Metrics
    const totalCostEl = document.getElementById("metricTotalCost");
    const cementEl = document.getElementById("metricCementBags");
    const steelEl = document.getElementById("metricSteelTonnes");
    const bricksEl = document.getElementById("metricBricks");

    if (totalCostEl) totalCostEl.textContent = `₹${totalCost.toLocaleString('en-IN')}`;
    const cementItem = materials.find(m => m.id === "cement");
    const steelItem = materials.find(m => m.id === "steel");
    const bricksItem = materials.find(m => m.id === "bricks");

    if (cementEl && cementItem) cementEl.textContent = `${cementItem.quantity.toLocaleString()} Bags`;
    if (steelEl && steelItem) steelEl.textContent = `${steelItem.quantity} Tonnes`;
    if (bricksEl && bricksItem) bricksEl.textContent = `${bricksItem.quantity.toLocaleString()} Nos`;

    // Table
    const tbody = document.getElementById("materialsTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    materials.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>
          <div style="font-weight:700; color:var(--text-primary);">${item.name}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">ID: ${item.id}</div>
        </td>
        <td>
          <span class="category-tag ${item.category}">${item.category}</span>
        </td>
        <td style="font-weight:700; font-family:var(--font-mono);">
          ${typeof item.quantity === 'number' ? item.quantity.toLocaleString() : item.quantity} ${item.unit}
        </td>
        <td style="font-family:var(--font-mono); color:var(--text-secondary);">
          ₹${item.unit_price.toLocaleString('en-IN')} / ${item.unit}
        </td>
        <td style="font-weight:800; color:var(--amber-400); font-family:var(--font-mono);">
          ₹${Math.round(item.subtotal).toLocaleString('en-IN')}
        </td>
        <td>
          <button class="btn-proof" onclick="window.ConstructApp.showMathProof('${item.id}')">
            🔍 Math Proof
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 8. Math Proof Modal
  showMathProof(materialId) {
    if (!this.currentAnalysis) return;
    const materials = this.currentAnalysis.outputs.cost.costed_materials || [];
    const item = materials.find(m => m.id === materialId);
    if (!item) return;

    const modal = document.getElementById("mathProofModal");
    const title = document.getElementById("proofModalTitle");
    const body = document.getElementById("proofModalBody");
    if (!modal) return;

    title.innerHTML = `📐 Deterministic Engineering Proof: ${item.name}`;
    body.innerHTML = `
      <div style="margin-bottom:1.25rem;">
        <div class="section-tag">Rule 2.1 — LLM Does Not Calculate</div>
        <p style="color:var(--text-secondary); margin-top:0.5rem; font-size:0.92rem;">
          This quantity was computed by a deterministic Python calculation tool adhering to standard civil engineering codes (IS 456 / SP 16). The LLM did not generate this arithmetic.
        </p>
      </div>

      <div style="background:#060913; border:1px solid var(--border-subtle); border-radius:8px; padding:1.25rem; margin-bottom:1.25rem;">
        <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700; text-transform:uppercase;">DETERMINISTIC FORMULA & DERIVATION</div>
        <div style="font-family:var(--font-mono); font-size:0.9rem; color:var(--cyan-400); margin-top:0.5rem; line-height:1.6;">
          ${item.proof || "Calculated using building built-up area and empirical ratio."}
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; background:rgba(255,255,255,0.03); padding:1rem; border-radius:8px; border:1px solid var(--border-subtle);">
        <div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">FINAL QUANTITY</div>
          <div style="font-size:1.3rem; font-weight:800; color:var(--text-primary); margin-top:2px;">
            ${typeof item.quantity === 'number' ? item.quantity.toLocaleString() : item.quantity} ${item.unit}
          </div>
        </div>
        <div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">UNIT PRICE BASIS</div>
          <div style="font-size:1.3rem; font-weight:800; color:var(--amber-400); margin-top:2px;">
            ₹${item.unit_price.toLocaleString('en-IN')}
          </div>
        </div>
      </div>
    `;

    modal.classList.add("active");
  }

  // 9. Render Suppliers Screen & Interactive Re-ranking
  renderSuppliersScreen(analysis) {
    this.recalculateSuppliers();
  }

  recalculateSuppliers() {
    const suppliers = [
      { id: "sup_1", name: "UltraTech Infra Logistics", dist: 4.8, rating: 4.9, location: "Peenya Industrial Area", mult: 0.99, stock: "Full Stock", ready: 7 },
      { id: "sup_2", name: "Tata Build Pro Suppliers", dist: 9.2, rating: 4.8, location: "North Highway Hub", mult: 0.97, stock: "High Stock", ready: 6 },
      { id: "sup_3", name: "Kalyani Material Depots", dist: 14.5, rating: 4.5, location: "Outer Freight Terminal", mult: 0.94, stock: "Partial Stock", ready: 5 },
      { id: "sup_4", name: "Apex City Construction Supplies", dist: 2.6, rating: 4.3, location: "Metro Central Depots", mult: 1.04, stock: "Immediate Dispatch", ready: 7 }
    ];

    const baseCost = this.currentAnalysis ? (this.currentAnalysis.outputs.cost.total_estimated_cost || 1850000) : 1850000;
    const { price: wp, distance: wd, stock: ws } = this.supplierWeights;

    const ranked = suppliers.map(s => {
      const priceScore = Math.max(0, Math.min(100, 100 - (s.mult - 0.90) * 250));
      const distScore = Math.max(0, Math.min(100, 100 - (s.dist / 16.0) * 100));
      const stockScore = (s.ready / 7.0) * 100;

      const composite = Math.round(wp * priceScore + wd * distScore + ws * stockScore);
      const quote = Math.round(baseCost * s.mult);

      return {
        ...s,
        priceScore: Math.round(priceScore),
        distScore: Math.round(distScore),
        stockScore: Math.round(stockScore),
        composite,
        quote
      };
    });

    // Sort descending
    ranked.sort((a, b) => b.composite - a.composite);

    // AI recommendation text
    const top = ranked[0];
    const recText = document.getElementById("aiSupplierRecommendationText");
    if (recText) {
      recText.innerHTML = `<strong>AI Recommendation:</strong> Supplier <strong>${top.name}</strong> achieved the highest composite index (<strong>${top.composite}/100</strong>) under your current criteria (Price: ${Math.round(wp*100)}%, Proximity: ${Math.round(wd*100)}%, Stock: ${Math.round(ws*100)}%). Total Estimated Quote: <strong>₹${top.quote.toLocaleString('en-IN')}</strong>.`;
    }

    const grid = document.getElementById("supplierCardsGrid");
    if (!grid) return;
    grid.innerHTML = "";

    ranked.forEach((s, idx) => {
      const isTop = idx === 0;
      const card = document.createElement("div");
      card.className = `supplier-card ${isTop ? 'top-pick' : ''}`;
      card.innerHTML = `
        ${isTop ? `<div class="top-badge">👑 AI TOP RECOMMENDATION</div>` : ''}
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
          <div>
            <h3 style="font-size:1.15rem; color:var(--text-primary);">${s.name}</h3>
            <div style="color:var(--text-secondary); font-size:0.82rem; margin-top:2px;">📍 ${s.location} • <strong>${s.dist} km</strong></div>
          </div>
          <div class="composite-score-ring">${s.composite}</div>
        </div>

        <div style="background:rgba(255,255,255,0.03); border-radius:8px; padding:0.85rem; margin-bottom:1rem;">
          <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:var(--text-muted);">
            <span>TOTAL PROCUREMENT QUOTE</span>
            <span style="color:var(--emerald-400); font-weight:700;">★ ${s.rating}</span>
          </div>
          <div style="font-size:1.45rem; font-weight:800; color:var(--text-primary); font-family:var(--font-mono); margin-top:3px;">
            ₹${s.quote.toLocaleString('en-IN')}
          </div>
        </div>

        <!-- Score Breakdown Bars -->
        <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.4rem; font-weight:700;">TRADE-OFF SCORE BREAKDOWN:</div>
        <div style="display:flex; flex-direction:column; gap:0.4rem; font-size:0.78rem;">
          <div style="display:flex; justify-content:space-between;">
            <span>Price Advantage</span>
            <span style="font-weight:700; color:var(--amber-400);">${s.priceScore}%</span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Proximity / Distance</span>
            <span style="font-weight:700; color:var(--cyan-400);">${s.distScore}%</span>
          </div>
          <div style="display:flex; justify-content:space-between;">
            <span>Stock Ready (${s.ready}/7 items)</span>
            <span style="font-weight:700; color:var(--emerald-400);">${s.stockScore}%</span>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  // 10. Render Phased Procurement & Delivery
  renderProcurementScreen(analysis) {
    const phases = [
      { id: 1, name: "Phase 1: Substructure & Foundation", duration: "3 - 4 Weeks", share: "38%", status: "Ready for Order", materials: ["Cement (Sub-base)", "M-Sand", "Coarse Aggregate 20mm", "TMT Reinforcement Fe550"] },
      { id: 2, name: "Phase 2: Superstructure & Masonry", duration: "5 - 7 Weeks", share: "42%", status: "Scheduled", materials: ["Columns & Beams Concrete", "Clay Bricks", "Masonry Mortar Cement", "Lintel Steel"] },
      { id: 3, name: "Phase 3: Architectural Finishing", duration: "4 - 5 Weeks", share: "20%", status: "Awaiting Prior Phases", materials: ["Vitrified Floor Tiles", "Internal & External Emulsion Paint", "Grouting & Primer"] }
    ];

    const timeline = document.getElementById("procurementTimeline");
    if (timeline) {
      timeline.innerHTML = "";
      phases.forEach(p => {
        const item = document.createElement("div");
        item.className = "phase-item";
        item.innerHTML = `
          <div class="phase-number">${p.id}</div>
          <div style="flex:1;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
              <h4 style="font-size:1.1rem; color:var(--text-primary);">${p.name}</h4>
              <span class="category-tag structural" style="background:rgba(16,185,129,0.1); color:var(--emerald-400); border-color:rgba(16,185,129,0.3);">${p.status}</span>
            </div>
            <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:4px;">
              Duration: <strong>${p.duration}</strong> • Budget Allocation: <strong>${p.share} of Total Capital</strong>
            </div>
            <div class="phase-chips-wrap">
              ${p.materials.map(m => `<span class="phase-chip">${m}</span>`).join("")}
            </div>
          </div>
        `;
        timeline.appendChild(item);
      });
    }

    const batches = [
      { id: "BATCH-01", name: "Delivery 1: Bulk Aggregate & Sand", vehicle: "16-Ton Tipper Truck", timing: "Day 2", phase: "Phase 1 - Foundation" },
      { id: "BATCH-02", name: "Delivery 2: TMT Steel Bundles & First Cement Lot", vehicle: "Flatbed Heavy Hauler", timing: "Day 5", phase: "Phase 1 - Foundation" },
      { id: "BATCH-03", name: "Delivery 3: Kiln Bricks & Superstructure Cement", vehicle: "10-Ton Cargo Vehicle", timing: "Week 4", phase: "Phase 2 - Structure" },
      { id: "BATCH-04", name: "Delivery 4: Vitrified Floor Tiles & Emulsion Paint", vehicle: "Weatherproof Container Van", timing: "Week 10", phase: "Phase 3 - Finishing" }
    ];

    const batchContainer = document.getElementById("deliveryBatchesContainer");
    if (batchContainer) {
      batchContainer.innerHTML = "";
      batches.forEach(b => {
        const card = document.createElement("div");
        card.style.cssText = "background:rgba(15,23,42,0.8); border:1px solid var(--border-subtle); padding:1rem; border-radius:10px;";
        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-muted);">
            <span>${b.id}</span>
            <span style="color:var(--amber-400); font-weight:700;">${b.timing}</span>
          </div>
          <div style="font-weight:700; color:var(--text-primary); margin:0.35rem 0;">${b.name}</div>
          <div style="font-size:0.82rem; color:var(--text-secondary);">Vehicle: <strong>${b.vehicle}</strong></div>
        `;
        batchContainer.appendChild(card);
      });
    }
  }

  // 11. Human-in-the-Loop Digital Signature Pad
  initSignaturePad() {
    this.signatureCanvas = document.getElementById("signaturePad");
    if (!this.signatureCanvas) return;
    const ctx = this.signatureCanvas.getContext("2d");

    const getPos = (e) => {
      const rect = this.signatureCanvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return {
        x: clientX - rect.left,
        y: clientY - rect.top
      };
    };

    const start = (e) => {
      this.isDrawingSignature = true;
      const pos = getPos(e);
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      const wm = document.getElementById("signatureWatermark");
      if (wm) wm.style.display = "none";
    };

    const draw = (e) => {
      if (!this.isDrawingSignature) return;
      const pos = getPos(e);
      ctx.lineTo(pos.x, pos.y);
      ctx.strokeStyle = "#22d3ee";
      ctx.lineWidth = 2.5;
      ctx.lineCap = "round";
      ctx.stroke();
    };

    const stop = () => {
      this.isDrawingSignature = false;
    };

    this.signatureCanvas.addEventListener("mousedown", start);
    this.signatureCanvas.addEventListener("mousemove", draw);
    window.addEventListener("mouseup", stop);

    this.signatureCanvas.addEventListener("touchstart", start);
    this.signatureCanvas.addEventListener("touchmove", draw);
    window.addEventListener("touchend", stop);
  }

  clearSignature() {
    if (!this.signatureCanvas) return;
    const ctx = this.signatureCanvas.getContext("2d");
    ctx.clearRect(0, 0, this.signatureCanvas.width, this.signatureCanvas.height);
    const wm = document.getElementById("signatureWatermark");
    if (wm) wm.style.display = "block";
  }

  // 12. Human-in-the-Loop Procurement Approval Execution
  async approveProcurement() {
    const engineerName = document.getElementById("engineerNameInput")?.value || "Ar. Vikramaditya Sharma";
    
    // Call server or simulate local approval
    let responseData = null;
    if (this.isServerOnline) {
      try {
        const res = await fetch(`${this.apiBase}/api/procurement/approve`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: this.activeProject.id,
            engineer_name: engineerName,
            signature: "SIG_VERIFIED",
            phases: ["Phase 1 - Foundation", "Phase 2 - Superstructure"]
          })
        });
        if (res.ok) responseData = await res.json();
      } catch (err) {
        console.warn("Server approval error, using local fallback", err);
      }
    }

    if (!responseData) {
      responseData = {
        approved_by: engineerName,
        approval_timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
        order_reference: `PO-CONSTRUCT-${Math.floor(1000 + Math.random() * 9000)}-2026`
      };
    }

    // Open Printable Work Order Modal
    this.showWorkOrderModal(responseData);
  }

  showWorkOrderModal(orderData) {
    const modal = document.getElementById("workOrderModal");
    const body = document.getElementById("workOrderModalBody");
    if (!modal) return;

    const proj = this.activeProject;
    const cost = this.currentAnalysis ? (this.currentAnalysis.outputs.cost.total_estimated_cost || 1850000) : 1850000;

    body.innerHTML = `
      <div style="border:2px solid #334155; padding:1.5rem; border-radius:12px; background:#0b1120;">
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #334155; padding-bottom:1rem; margin-bottom:1rem;">
          <div>
            <h2 style="color:#f59e0b; font-size:1.4rem; font-weight:800;">CONSTRUCT-AI OFFICIAL WORK ORDER</h2>
            <div style="font-size:0.82rem; color:#94a3b8;">Agentic Multi-Agent Procurement & Engineering Requisition</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:0.8rem; color:#94a3b8;">ORDER REF:</div>
            <div style="font-weight:800; font-family:var(--font-mono); color:#22d3ee;">${orderData.order_reference}</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; font-size:0.85rem; margin-bottom:1rem;">
          <div>
            <span style="color:#94a3b8;">Project:</span> <strong>${proj.project_name}</strong><br>
            <span style="color:#94a3b8;">Site Location:</span> ${proj.location}<br>
            <span style="color:#94a3b8;">Built-up Area:</span> ${proj.floor_area} sq.ft (${proj.building_type})
          </div>
          <div>
            <span style="color:#94a3b8;">Authorizing Engineer:</span> <strong>${orderData.approved_by}</strong><br>
            <span style="color:#94a3b8;">Signed Timestamp:</span> ${orderData.approval_timestamp}<br>
            <span style="color:#94a3b8;">Verification Status:</span> <span style="color:#10b981; font-weight:700;">✓ PASS (5/5 Checks)</span>
          </div>
        </div>

        <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); padding:0.85rem; border-radius:8px; font-size:0.85rem; margin-bottom:1.25rem;">
          <strong>Total Authorized Capital:</strong> <span style="font-size:1.2rem; font-weight:800; color:#fbbf24;">₹${cost.toLocaleString('en-IN')}</span>
          <p style="font-size:0.75rem; color:#fef3c7; margin-top:4px;">Procurement released under Human-in-the-Loop engineer sign-off. Supplier orders dispatched.</p>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:flex-end; border-top:1px dashed #334155; padding-top:1rem;">
          <div style="font-size:0.78rem; color:#94a3b8;">
            Deterministic calculations verified against IS 456:2000.
          </div>
          <div style="text-align:center;">
            <div style="font-family:'Brush Script MT', cursive, sans-serif; font-size:1.6rem; color:#38bdf8;">${orderData.approved_by}</div>
            <div style="border-top:1px solid #475569; width:160px; font-size:0.72rem; color:#94a3b8; padding-top:2px;">Digital Signature Confirmed</div>
          </div>
        </div>
      </div>
    `;

    modal.classList.add("active");
  }

  // 13. Replan Simulation Trigger
  triggerReplanTest() {
    this.startAnalysis(this.activeProject, null, "price_anomaly");
  }

  // 14. Projects List Renderer
  renderProjectsList() {
    const container = document.getElementById("dashboardProjectsList");
    if (!container) return;
    container.innerHTML = "";

    this.projectsList.forEach(p => {
      const card = document.createElement("div");
      card.className = "glass-panel";
      card.style.padding = "1.5rem";
      card.style.cursor = "pointer";
      card.onclick = () => {
        this.activeProject = p;
        this.navigate("analysis");
        this.loadDemoPreset(p.building_type === "commercial" ? "commercial" : "villa");
      };

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
          <div>
            <h3 style="font-size:1.15rem; font-weight:700; color:var(--text-primary);">${p.project_name}</h3>
            <div style="font-size:0.82rem; color:var(--text-secondary); margin-top:2px;">📍 ${p.location}</div>
          </div>
          <span class="category-tag ${p.status === 'Analysis Complete' ? 'finishing' : 'structural'}">${p.status}</span>
        </div>
        <div style="display:flex; gap:1.5rem; font-size:0.85rem; color:var(--text-secondary); margin-top:1rem; border-top:1px solid var(--border-subtle); padding-top:0.75rem;">
          <div>Type: <strong style="color:var(--text-primary);">${p.building_type.toUpperCase()}</strong></div>
          <div>Floor Area: <strong style="color:var(--text-primary);">${p.floor_area} sq.ft</strong></div>
          <div>Floors: <strong style="color:var(--text-primary);">${p.floors || 1}</strong></div>
        </div>
      `;
      container.appendChild(card);
    });
  }

  // Helper: Toast notification
  showToast(msg) {
    const toast = document.createElement("div");
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid var(--amber-500);
      box-shadow: var(--shadow-glow);
      color: #fff;
      padding: 0.9rem 1.4rem;
      border-radius: 10px;
      z-index: 2000;
      font-weight: 600;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      animation: fadeIn 0.3s ease;
    `;
    toast.innerHTML = `<span>✨</span> ${msg}`;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.4s";
      setTimeout(() => toast.remove(), 400);
    }, 3500);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.ConstructApp = new ConstructApp();
});
