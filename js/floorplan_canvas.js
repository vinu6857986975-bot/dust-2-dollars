/**
 * Construct-AI — Interactive Floor Plan Canvas & Vision Scanner
 * Renders technical architectural blueprints, laser scan lines, and detected room bounding boxes.
 */

class FloorPlanVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.currentPreset = "villa";
    this.activeLayer = "architectural"; // 'architectural' | 'structural' | 'materials'
    this.isScanning = false;
    this.scanProgress = 0;
    this.detectedBoxes = [];
    this.animationFrame = null;

    this.initResize();
  }

  initResize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const width = rect.width || 800;
    const height = 420;

    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;

    this.ctx.scale(dpr, dpr);
    this.width = width;
    this.height = height;
    this.render();
  }

  loadPreset(presetKey) {
    this.currentPreset = presetKey;
    const preset = window.CONSTRUCT_DATA.presets[presetKey] || window.CONSTRUCT_DATA.presets.villa;
    this.detectedBoxes = preset.cad_rooms || [];
    this.render();
  }

  setLayer(layer) {
    this.activeLayer = layer;
    this.render();
  }

  startScanning(onComplete) {
    this.isScanning = true;
    this.scanProgress = 0;
    const laserEl = document.getElementById("laserScannerLine");
    if (laserEl) laserEl.classList.add("scanning");

    const startTime = performance.now();
    const duration = 2800; // 2.8s scan simulation

    const animate = (time) => {
      const elapsed = time - startTime;
      this.scanProgress = Math.min(1, elapsed / duration);
      this.render();

      if (this.scanProgress < 1) {
        this.animationFrame = requestAnimationFrame(animate);
      } else {
        this.isScanning = false;
        if (laserEl) laserEl.classList.remove("scanning");
        if (onComplete) onComplete();
      }
    };
    this.animationFrame = requestAnimationFrame(animate);
  }

  render() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    // 1. Clear & Background Grid (Architectural Blueprint Slate)
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "#050811";
    ctx.fillRect(0, 0, w, h);

    // Subtle CAD Grid
    ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    ctx.lineWidth = 1;
    const gridSize = 25;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    const preset = window.CONSTRUCT_DATA.presets[this.currentPreset] || window.CONSTRUCT_DATA.presets.villa;
    const rooms = preset.cad_rooms || [];

    // Center offset
    const scale = Math.min((w - 80) / 600, (h - 80) / 450);
    const offsetX = (w - 600 * scale) / 2;
    const offsetY = (h - 450 * scale) / 2;

    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    // 2. Exterior Perimeter Outline
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 4;
    ctx.strokeRect(40, 40, 520, 370);

    // 3. Render Rooms / Detected Zones
    rooms.forEach((room, idx) => {
      // If scanning, show progressively
      const isVisible = !this.isScanning || (this.scanProgress >= (idx + 1) / (rooms.length + 1));
      if (!isVisible) return;

      if (this.activeLayer === "architectural" || this.activeLayer === "materials") {
        // Room Fill
        ctx.fillStyle = this.activeLayer === "materials" ? "rgba(245, 158, 11, 0.12)" : "rgba(30, 41, 59, 0.55)";
        ctx.fillRect(room.x, room.y, room.w, room.h);

        // Room Wall Borders
        ctx.strokeStyle = this.activeLayer === "materials" ? "#f59e0b" : "#38bdf8";
        ctx.lineWidth = 2;
        ctx.strokeRect(room.x, room.y, room.w, room.h);

        // Room Text
        ctx.fillStyle = "#f8fafc";
        ctx.font = "bold 13px Inter, sans-serif";
        ctx.fillText(room.name, room.x + 12, room.y + 26);

        ctx.fillStyle = "#94a3b8";
        ctx.font = "11px Inter, sans-serif";
        ctx.fillText(`${room.area_sqft} sq.ft`, room.x + 12, room.y + 44);

        // Door Arc
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(room.x + 25, room.y + room.h, 18, Math.PI, 1.5 * Math.PI);
        ctx.stroke();
      }

      // Structural Layer (Columns and Beams)
      if (this.activeLayer === "structural") {
        ctx.fillStyle = "rgba(15, 23, 42, 0.4)";
        ctx.fillRect(room.x, room.y, room.w, room.h);

        // Grid Beams
        ctx.strokeStyle = "#6366f1";
        ctx.lineWidth = 3;
        ctx.setLineDash([6, 4]);
        ctx.strokeRect(room.x, room.y, room.w, room.h);
        ctx.setLineDash([]);

        // Columns at corners (RCC Columns)
        const corners = [
          [room.x, room.y],
          [room.x + room.w, room.y],
          [room.x, room.y + room.h],
          [room.x + room.w, room.y + room.h]
        ];
        ctx.fillStyle = "#f43f5e";
        corners.forEach(([cx, cy]) => {
          ctx.fillRect(cx - 5, cy - 5, 10, 10);
        });

        // Column annotation
        ctx.fillStyle = "#a5b4fc";
        ctx.font = "10px JetBrains Mono, monospace";
        ctx.fillText("C1 300x450mm RCC", room.x + 10, room.y + 20);
      }

      // Detection HUD Bounding Box Highlight
      if (this.isScanning && isVisible) {
        ctx.strokeStyle = "#22d3ee";
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 2]);
        ctx.strokeRect(room.x - 2, room.y - 2, room.w + 4, room.h + 4);
        ctx.setLineDash([]);
      }
    });

    // 4. North Arrow & Scale Bar
    ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
    ctx.font = "bold 11px Inter, sans-serif";
    ctx.fillText("▲ N", 530, 70);
    ctx.font = "9px Inter, sans-serif";
    ctx.fillText("SCALE: 1:100", 40, 435);

    ctx.restore();
  }
}

window.FloorPlanVisualizer = FloorPlanVisualizer;
