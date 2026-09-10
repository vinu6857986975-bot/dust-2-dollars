/**
 * Construct-AI — Demo Presets & Architectural Data Models
 */

window.CONSTRUCT_DATA = {
  presets: {
    hyderabad_2bhk: {
      id: "hyderabad_2bhk",
      name: "2BHK Residential House — Hyderabad (Official MVP)",
      building_type: "residential",
      built_up_area: 1500,
      plot_area: 2400,
      floors: 1,
      location: "Gachibowli, Hyderabad, Telangana",
      confidence: 0.87,
      description: "Official MVP Demo: 2-BHK residential single-storey house in Hyderabad with hall, 2 bedrooms, kitchen, 2 baths, and portico.",
      rooms: 5,
      doors: 4,
      windows: 6,
      cad_rooms: [
        { name: "Living & Hall", area_sqft: 450, x: 50, y: 50, w: 260, h: 180, color: "#38bdf8" },
        { name: "Kitchen & Dining", area_sqft: 280, x: 320, y: 50, w: 200, h: 180, color: "#4ade80" },
        { name: "Master Bedroom", area_sqft: 380, x: 50, y: 240, w: 230, h: 190, color: "#fbbf24" },
        { name: "Bedroom 2", area_sqft: 250, x: 290, y: 240, w: 140, h: 190, color: "#a78bfa" },
        { name: "Attached Bath & Utility", area_sqft: 140, x: 440, y: 240, w: 80, h: 190, color: "#f472b6" }
      ]
    },
    villa: {
      id: "villa",
      name: "Skyline Luxury Villa (4-BHK)",
      building_type: "residential",
      built_up_area: 2400,
      plot_area: 4000,
      floors: 2,
      location: "Indiranagar, Bangalore, India",
      confidence: 0.89,
      description: "Two-storey contemporary villa featuring 4 en-suite bedrooms, open living-dining pavilion, and portico.",
      rooms: 5,
      doors: 8,
      windows: 10,
      cad_rooms: [
        { name: "Living & Foyer", area_sqft: 650, x: 50, y: 50, w: 240, h: 180, color: "#38bdf8" },
        { name: "Dining & Open Kitchen", area_sqft: 450, x: 310, y: 50, w: 200, h: 180, color: "#4ade80" },
        { name: "Master Suite", area_sqft: 520, x: 50, y: 250, w: 220, h: 180, color: "#fbbf24" },
        { name: "Guest Bedroom 1", area_sqft: 380, x: 290, y: 250, w: 150, h: 180, color: "#a78bfa" },
        { name: "Utility & Bath", area_sqft: 200, x: 460, y: 250, w: 120, h: 180, color: "#f472b6" },
        { name: "Verandah / Deck", area_sqft: 200, x: 50, y: 450, w: 530, h: 60, color: "#94a3b8" }
      ]
    },
    commercial: {
      id: "commercial",
      name: "TechPark Commercial Annex",
      building_type: "commercial",
      built_up_area: 5200,
      plot_area: 8500,
      floors: 1,
      location: "Electronic City Phase 1, Bangalore",
      confidence: 0.84,
      description: "Grade-A open floor office shell with central core, meeting clusters, and server hub.",
      rooms: 12,
      doors: 14,
      windows: 22,
      cad_rooms: [
        { name: "Open Workstation Hall", area_sqft: 2800, x: 50, y: 50, w: 320, h: 260, color: "#38bdf8" },
        { name: "Executive Suites", area_sqft: 900, x: 390, y: 50, w: 190, h: 140, color: "#fbbf24" },
        { name: "Conference Room A & B", area_sqft: 750, x: 390, y: 210, w: 190, h: 100, color: "#a78bfa" },
        { name: "Cafeteria & Pantry", area_sqft: 500, x: 50, y: 330, w: 260, h: 150, color: "#4ade80" },
        { name: "Server & Restrooms", area_sqft: 250, x: 330, y: 330, w: 250, h: 150, color: "#f472b6" }
      ]
    },
    apartment: {
      id: "apartment",
      name: "Emerald Urban Duplex Residence",
      building_type: "residential",
      built_up_area: 1250,
      plot_area: 2200,
      floors: 1,
      location: "Whitefield Tech Corridor, Bangalore",
      confidence: 0.92,
      description: "Optimized 2-BHK apartment layout with utility balcony and compact circulation.",
      rooms: 3,
      doors: 5,
      windows: 6,
      cad_rooms: [
        { name: "Living Room", area_sqft: 480, x: 60, y: 60, w: 260, h: 200, color: "#38bdf8" },
        { name: "Kitchenette", area_sqft: 220, x: 340, y: 60, w: 180, h: 140, color: "#4ade80" },
        { name: "Master Bedroom", area_sqft: 350, x: 60, y: 280, w: 260, h: 180, color: "#fbbf24" },
        { name: "Kids Room & Bath", area_sqft: 200, x: 340, y: 220, w: 180, h: 240, color: "#a78bfa" }
      ]
    },
    low_confidence_sample: {
      id: "low_confidence_sample",
      name: "Heritage Site Renovation (Low Confidence)",
      building_type: "residential",
      built_up_area: 950,
      plot_area: 1600,
      floors: 1,
      location: "Old Town Heritage Zone, Mysore",
      confidence: 0.52, // < 0.6 triggers manual fallback
      description: "Low-angle mobile snapshot with perspective distortion. Prompts engineer verification.",
      rooms: 2,
      doors: 3,
      windows: 4,
      cad_rooms: [
        { name: "Uncertain Perimeter A", area_sqft: 550, x: 80, y: 80, w: 240, h: 220, color: "#f87171" },
        { name: "Uncertain Perimeter B", area_sqft: 400, x: 340, y: 120, w: 180, h: 180, color: "#f87171" }
      ]
    }
  },

  initialProjects: [
    {
      id: 1,
      project_name: "Skyline Luxury Villa (4-BHK)",
      building_type: "residential",
      floor_area: 2400,
      plot_area: 4000,
      floors: 2,
      location: "Indiranagar, Bangalore, India",
      status: "Analysis Complete",
      created_at: "2026-09-07 14:30"
    },
    {
      id: 2,
      project_name: "TechPark Commercial Annex",
      building_type: "commercial",
      floor_area: 5200,
      plot_area: 8500,
      floors: 1,
      location: "Electronic City Phase 1, Bangalore",
      status: "Analysis Complete",
      created_at: "2026-09-06 11:15"
    },
    {
      id: 3,
      project_name: "Emerald Urban Duplex Residence",
      building_type: "residential",
      floor_area: 1250,
      plot_area: 2200,
      floors: 1,
      location: "Whitefield Tech Corridor, Bangalore",
      status: "In Progress",
      created_at: "2026-09-08 09:40"
    }
  ]
};
