/**
 * Construct-AI — Deterministic Client-side Calculation Engine & Math Proofs
 * Standard: IS 456:2000, IS 1786, SP 16 Design Aids
 * Rule 2.1: LLM Does Not Calculate
 */

window.ConstructCalculations = {
  // 1. Concrete Volume Calculation
  calculateConcreteVolume(builtUpAreaSqft, floors = 1, buildingType = "residential") {
    const areaSqm = builtUpAreaSqft * 0.092903;
    const totalBuiltUpSqm = areaSqm * floors;
    const factor = buildingType.toLowerCase() === "residential" ? 0.22 : 0.28;
    const concreteVolumeM3 = parseFloat((totalBuiltUpSqm * factor).toFixed(2));

    return {
      builtUpAreaSqm: parseFloat(totalBuiltUpSqm.toFixed(2)),
      concreteVolumeM3,
      formula: "Total Built-up Area (m²) × Concrete Index (m³/m²)",
      proof: `${totalBuiltUpSqm.toFixed(2)} m² built-up × ${factor} m³/m² (IS 456 standard empirical coefficient) = ${concreteVolumeM3.toFixed(2)} m³ total concrete volume`
    };
  },

  // 2. Mix Design: Cement, Sand, Coarse Aggregate
  calculateMixDesign(concreteVolumeM3, mixRatio = "M20") {
    const ratios = {
      "M15": { c: 1, s: 2, a: 4, sum: 7.0 },
      "M20": { c: 1, s: 1.5, a: 3, sum: 5.5 },
      "M25": { c: 1, s: 1, a: 2, sum: 4.0 }
    };
    const r = ratios[mixRatio] || ratios["M20"];
    const dryVolume = parseFloat((concreteVolumeM3 * 1.54).toFixed(2));

    // Cement in bags (1 bag = 50kg, cement density = 1440 kg/m3)
    const cementVolumeM3 = (r.c / r.sum) * dryVolume;
    const cementKg = cementVolumeM3 * 1440;
    const cementBags = Math.ceil(cementKg / 50);

    // Sand (m3)
    const sandM3 = parseFloat(((r.s / r.sum) * dryVolume).toFixed(2));

    // Aggregate (m3)
    const aggregateM3 = parseFloat(((r.a / r.sum) * dryVolume).toFixed(2));

    return {
      mixRatio,
      dryVolumeM3: dryVolume,
      cementBags,
      sandM3,
      aggregateM3,
      formula: "Dry Volume = Wet Volume × 1.54 (Void Factor). Material = (Parts / Sum Parts) × Dry Volume",
      proof: `Dry Volume = ${concreteVolumeM3} m³ × 1.54 = ${dryVolume} m³. Mix ${mixRatio} (1 : ${r.s} : ${r.a}). Cement Bags = (${r.c}/${r.sum}) × ${dryVolume} × 1440 / 50 = ${cementBags} Bags. Fine Sand = ${sandM3} m³. Coarse Aggregate = ${aggregateM3} m³.`
    };
  },

  // 3. Steel Reinforcement Requirement
  calculateSteelRequirement(concreteVolumeM3, buildingType = "residential") {
    const kgPerM3 = buildingType.toLowerCase() === "residential" ? 82 : 96;
    const totalSteelKg = parseFloat((concreteVolumeM3 * kgPerM3).toFixed(2));
    const totalSteelTonnes = parseFloat((totalSteelKg / 1000.0).toFixed(3));

    return {
      steelKg: totalSteelKg,
      steelTonnes: totalSteelTonnes,
      kgPerM3,
      formula: "Concrete Volume (m³) × Steel Reinforcement Density Index (kg/m³)",
      proof: `${concreteVolumeM3.toFixed(2)} m³ concrete × ${kgPerM3} kg/m³ steel (IS 1786 Fe550 rebar schedule) = ${totalSteelKg.toFixed(2)} kg (${totalSteelTonnes.toFixed(3)} Tonnes)`
    };
  },

  // 4. Brick Masonry Requirement
  calculateBrickwork(builtUpAreaSqft, floors = 1, ceilingHeightM = 3.0) {
    const areaSqm = builtUpAreaSqft * 0.092903;
    const perimeterM = 4 * Math.sqrt(areaSqm) * 1.35;
    const wallHeightM = ceilingHeightM * floors;
    const wallThicknessM = 0.23; // 9-inch wall

    const grossWallVolumeM3 = perimeterM * wallHeightM * wallThicknessM;
    const netWallVolumeM3 = parseFloat((grossWallVolumeM3 * 0.85).toFixed(2)); // 15% opening deduction

    const rawBricks = netWallVolumeM3 * 500;
    const totalBricks = Math.ceil(rawBricks * 1.05); // 5% site handling wastage

    const mortarDryVol = (netWallVolumeM3 * 0.25) * 1.33;
    const masonryCementBags = Math.ceil((1 / 7) * mortarDryVol * 1440 / 50);
    const masonrySandM3 = parseFloat(((6 / 7) * mortarDryVol).toFixed(2));

    return {
      totalBricks,
      netWallVolumeM3,
      masonryCementBags,
      masonrySandM3,
      formula: "Net Masonry Volume (m³) × 500 Bricks/m³ + 5% Wastage Allowance",
      proof: `Net Wall Volume = ${netWallVolumeM3} m³ (after 15% door/window deductions). 500 modular bricks/m³ × 1.05 wastage = ${totalBricks.toLocaleString()} Nos. Mortar (1:6) requires ${masonryCementBags} bags cement & ${masonrySandM3} m³ sand.`
    };
  },

  // 5. Finishing: Tiles & Paint
  calculateFinishing(builtUpAreaSqft, floors = 1) {
    const totalFloorSqft = builtUpAreaSqft * floors;
    const tilesSqft = Math.ceil(totalFloorSqft * 1.08); // 8% cutting wastage

    const paintableAreaSqft = parseFloat((totalFloorSqft * 3.6).toFixed(1));
    const paintLitres = Math.ceil(paintableAreaSqft / 75.0); // 75 sq.ft per litre for 2 coats + primer

    return {
      tilesSqft,
      paintableAreaSqft,
      paintLitres,
      formula: "Tiles = Floor Area × 1.08. Paint = Wall/Ceiling Area (3.6 × Floor) ÷ 75 sq.ft/L (2 coats)",
      proof: `Flooring: ${totalFloorSqft} sq.ft × 1.08 = ${tilesSqft.toLocaleString()} sq.ft. Paintable Surface = ${paintableAreaSqft} sq.ft ÷ 75 sq.ft/L = ${paintLitres} Litres emulsion.`
    };
  }
};
