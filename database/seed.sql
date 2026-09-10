-- Construct-AI Seed Data

-- 1. Default User
INSERT OR IGNORE INTO users (id, name, email, password_hash, role)
VALUES (1, 'Ar. Vikramaditya Sharma', 'vikram@construct-ai.io', 'demo_hash', 'Principal Structural Lead');

-- 2. Materials
INSERT OR IGNORE INTO materials (id, name, unit, category) VALUES
('cement', 'OPC 53 Grade Cement', 'Bags', 'structural'),
('sand', 'Manufactured River Sand (M-Sand)', 'm³', 'structural'),
('aggregate', 'Graded Coarse Aggregate (20mm)', 'm³', 'structural'),
('steel', 'TMT Rebars Fe550 Grade', 'Tonnes', 'structural'),
('bricks', 'Standard Kiln-Baked Red Bricks', 'Nos', 'masonry'),
('tiles', 'Vitrified Glazed Floor Tiles (600x600mm)', 'sq.ft', 'finishing'),
('paint', 'Premium Interior & Exterior Emulsion', 'Litres', 'finishing');

-- 3. Suppliers
INSERT OR IGNORE INTO suppliers (id, name, phone, address, distance_km, latitude, longitude, rating) VALUES
('sup_1', 'UltraTech Infra Logistics', '+91 80 2839 1100', 'Plot 42, Peenya Industrial Area, Phase 2, Bangalore', 4.8, 13.0285, 77.5190, 4.9),
('sup_2', 'Tata Build Pro Suppliers', '+91 80 4112 5590', 'NH 44, North Highway Hub, Yelahanka, Bangalore', 9.2, 13.1007, 77.5963, 4.8),
('sup_3', 'Kalyani Material Depots', '+91 80 2658 9012', 'Outer Freight Terminal, Hosur Road, Bangalore', 14.5, 12.8750, 77.6710, 4.5),
('sup_4', 'Apex City Construction Supplies', '+91 80 2553 4401', 'Old Madras Road, Central Depots, Bangalore', 2.6, 12.9780, 77.6320, 4.3);

-- 4. Material Prices (INR ₹ per unit)
-- UltraTech
INSERT OR IGNORE INTO material_prices (material_id, supplier_id, price) VALUES
('cement', 'sup_1', 385.0),
('sand', 'sup_1', 1910.0),
('aggregate', 'sup_1', 1680.0),
('steel', 'sup_1', 63850.0),
('bricks', 'sup_1', 9.60),
('tiles', 'sup_1', 72.0),
('paint', 'sup_1', 355.0);

-- Tata Build Pro
INSERT OR IGNORE INTO material_prices (material_id, supplier_id, price) VALUES
('cement', 'sup_2', 375.0),
('sand', 'sup_2', 2025.0),
('aggregate', 'sup_2', 1585.0),
('steel', 'sup_2', 62560.0),
('bricks', 'sup_2', 9.30),
('tiles', 'sup_2', 68.5),
('paint', 'sup_2', 335.0);

-- Kalyani
INSERT OR IGNORE INTO material_prices (material_id, supplier_id, price) VALUES
('cement', 'sup_3', 362.0),
('sand', 'sup_3', 1850.0),
('aggregate', 'sup_3', 1550.0),
('steel', 'sup_3', 61920.0),
('bricks', 'sup_3', 8.75),
('tiles', 'sup_3', 79.0),
('paint', 'sup_3', 320.0);

-- Apex City
INSERT OR IGNORE INTO material_prices (material_id, supplier_id, price) VALUES
('cement', 'sup_4', 400.0),
('sand', 'sup_4', 1990.0),
('aggregate', 'sup_4', 1700.0),
('steel', 'sup_4', 67700.0),
('bricks', 'sup_4', 9.90),
('tiles', 'sup_4', 74.0),
('paint', 'sup_4', 345.0);

-- 5. Seed Projects
INSERT OR IGNORE INTO projects (id, user_id, project_name, building_type, plot_area, floor_area, floors, location, status) VALUES
(1, 1, 'Skyline Luxury Villa (4-BHK)', 'residential', 4000.0, 2400.0, 2, 'Indiranagar, Bangalore', 'Analysis Complete'),
(2, 1, 'TechPark Commercial Annex', 'commercial', 8500.0, 5200.0, 1, 'Electronic City Phase 1, Bangalore', 'Analysis Complete'),
(3, 1, 'Emerald Urban Duplex Residence', 'residential', 2200.0, 1250.0, 1, 'Whitefield Tech Corridor, Bangalore', 'In Progress');
