# 🏗️ Construct-AI — Autonomous Multi-Agent Construction Planning Platform

An interactive, responsive, and production-ready **Agentic Construction Planning Platform** built strictly in accordance with the official **Construct-AI System Architecture**, **Agent Design Specification**, and **Frontend Page Specification**.

---

## 🎨 UI & UX Design System & Color Palette

Construct-AI features an architectural, high-tech AI design system tailored for engineering professionals:

| UI Role | Color Name | Hex Code | Visual Application |
| :--- | :--- | :--- | :--- |
| **Primary Brand** | Industrial Safety Gold | `#F59E0B` / `#D97706` | Primary action buttons, badges, key figures |
| **Accent Glow** | Construction Amber | `#FFB020` / `#F97316` | Active agent aura, laser sweep line |
| **Canvas Background** | Blueprint Slate Navy | `#070A12` | Deep contrast background with subtle CAD grid |
| **Card Surface** | Frosted Slate Glass | `rgba(15, 23, 42, 0.78)` | Translucent glassmorphism with 1px border |
| **Stage 1 (Foundation)** | Earth Amber | `#D97706` | Footing, sub-structure, excavation phase |
| **Stage 2 (Structure)** | Industrial Cyan/Indigo | `#3B82F6` / `#6366F1` | Columns, beams, slabs, brick masonry |
| **Stage 3 (Finishing)** | Architect Emerald | `#10B981` | Vitrified tiles, emulsion paint, fittings |
| **Verification Pass** | Emerald Verified | `#10B981` | Passed 5-point engineering checklist |
| **Sanity Violation** | Crimson Alert | `#EF4444` | Price surge / mix ratio anomaly warning |

---

## 🤖 9 Directed LangGraph Agents

The system orchestrates 9 specialized agents in a directed state machine:

1. **🎯 Intent Agent**: Classifies project specifications, determines analysis mode, and passes structured intent.
2. **👁️ Vision Agent**: Analyzes 2D architectural floor plans / photographs to detect rooms, doors, windows, and calculate spatial area. If confidence drops below `0.60`, it triggers a mandatory manual dimension verification banner.
3. **📐 Estimation Agent**: Calls deterministic Python calculation functions in `calculations/engine.py` (adhering to **Rule 2.1: LLM Does Not Calculate**).
4. **📦 Material Agent**: Normalizes raw engineering quantities into a categorized Bill of Materials (BOM) with standardized civil units.
5. **💰 Cost Agent**: Evaluates pricing in Indian Rupees (₹ INR) sourced directly from the seeded `material_prices` table.
6. **🚚 Supplier Agent**: Multi-criteria trade-off scoring evaluating price competitiveness, logistics distance (km), and real-time inventory availability.
7. **📅 Planning Agent**: Generates a 3-phase procurement timeline (Substructure & Foundation, Superstructure & Masonry, Architectural Finishing).
8. **🚛 Delivery Agent**: Batches heavy building materials into vehicle consignments based on truck tonnage capacities and phase dependency.
9. **🛡️ Verification Agent & Orchestrator**: Executes a 5-point civil engineering sanity checklist. If a price anomaly or mix ratio violation is detected, it triggers a bounded replanning loop (Attempt 1 of 2) without restarting the entire pipeline.

---

## 📐 Rule 2.1: Deterministic Civil Calculations (IS 456 / SP 16)

> *"The LLM never performs engineering calculations or pricing arithmetic directly."*

- **Concrete Volume**: Empirically estimated per IS 456 coefficients ($0.22\text{ m}^3/\text{m}^2$ for residential, $0.28\text{ m}^3/\text{m}^2$ for commercial).
- **Cement, Sand & Aggregate**: Standard dry volume conversion factor of `1.54` with M20 mix ratio (`1 : 1.5 : 3`).
- **Steel Reinforcement**: $82\text{ kg/m}^3$ (residential) to $96\text{ kg/m}^3$ (commercial) Fe550 high-yield rebars.
- **Brick Masonry**: 500 modular bricks per $\text{m}^3$ of net wall volume with a 15% opening deduction and 5% handling wastage.
- **Math Proof Inspector**: Every line item in the Material Table has a **"🔍 Math Proof"** button that reveals the full step-by-step mathematical derivation.

---

## ⚡ Zero-Dependency Dual-Mode Architecture

Construct-AI is designed to run under **any** environment with zero friction:

### Option 1: Full REST API + SQLite Backend (Recommended)
Runs using Python 3's standard library with **zero pip dependencies**:

```powershell
python server.py
```
- Open your browser at: **`http://localhost:8000`**
- API Health Endpoint: `http://localhost:8000/api/health`
- REST Endpoints for Projects, Analysis, Replan simulation, Suppliers, Procurement, and Logs.

### Option 2: Standalone Local Engine (Zero Setup)
- Double-click `index.html` to open directly in any web browser (`file:///.../index.html`).
- The application automatically detects offline mode and runs the full client-side deterministic calculation engine, interactive CAD canvas, multi-agent state visualizer, and supplier re-ranker.

---

## 🧪 Testing Checklist & Demo Verification

- [x] **Upload & Presets**: 1-click presets for Luxury Villa (4-BHK), Commercial Space, Duplex Apartment, or Low Confidence photo.
- [x] **Vision Scanner & Canvas**: Animated laser sweep line, detected room boxes, and layer toggles (Architectural, Structural RCC Grid, Material Heatmap).
- [x] **Low Confidence Fallback**: When confidence is below 60%, a manual dimension override prompt is displayed.
- [x] **Deterministic Traceability**: Click **"🔍 Math Proof"** on any material item to view the exact formula and IS 456 coefficients.
- [x] **Interactive Supplier Weights**: Adjust sliders for Price %, Distance %, and Stock % to watch the supplier cards re-rank in real time.
- [x] **Replan Loop Simulation**: Click **"⚡ Simulate Verification Failure & Replan"** to observe the Verification Agent catch a steel price surge and trigger a bounded replan loop live.
- [x] **Real-Time Agent Audit Log**: Live streaming console showing each agent firing in sequence with tool inputs and JSON outputs.
- [x] **Human-in-the-Loop Gate**: Interactive digital signature canvas pad and official printable Purchase Order voucher (`Ctrl + P`).
- [x] **Engineering Disclaimer**: Prominent safety notice displayed on all cost and material pages.
