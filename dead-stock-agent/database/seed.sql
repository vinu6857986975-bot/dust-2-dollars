-- ============================================================
-- DUST 2 DOLLAR — Seed Data
-- 30 realistic demo products with varied aging scenarios
-- ============================================================

-- ─── Categories ──────────────────────────────────────────────
INSERT OR IGNORE INTO categories (name, seasonality, avg_shelf_days, dead_threshold_days) VALUES
('Apparel', 'none', 90, 60),
('Footwear', 'none', 75, 50),
('Electronics', 'none', 120, 90),
('Grocery', 'none', 30, 20),
('Toys & Games', 'festive', 60, 45),
('Sports & Fitness', 'summer', 90, 60),
('Home & Kitchen', 'none', 120, 90),
('Books & Stationery', 'none', 180, 120),
('Winter Wear', 'winter', 60, 40),
('Beauty & Personal Care', 'none', 90, 60);

-- ─── Suppliers ───────────────────────────────────────────────
INSERT OR IGNORE INTO suppliers (name, contact_email, return_allowed, return_window_days, refund_type, exchange_allowed, penalty_pct) VALUES
('FastFashion Wholesale', 'supply@fastfashion.com', 1, 30, 'credit', 1, 5.0),
('TechGadget Distributors', 'ops@techgadget.in', 1, 60, 'full', 0, 0.0),
('FoodHub Logistics', 'fhl@foodhub.com', 0, 0, 'none', 0, 0.0),
('PlayZone Imports', 'returns@playzone.com', 1, 45, 'partial', 1, 10.0),
('ProSports Supply Co.', 'support@prosports.in', 1, 90, 'full', 1, 0.0),
('HomeStyle Vendors', 'hs@homestyle.com', 0, 0, 'none', 0, 0.0),
('BookWorld Distributors', 'bw@bookworld.in', 0, 0, 'none', 0, 0.0),
('WinterWear Wholesale', 'ww@winterwear.com', 1, 20, 'credit', 0, 15.0),
('GlowBeauty Supply', 'gb@glowbeauty.in', 1, 30, 'partial', 1, 5.0),
('SportKicks Imports', 'sk@sportkicks.com', 1, 45, 'full', 1, 0.0);

-- ─── Products & Inventory (30 items) ─────────────────────────
INSERT OR IGNORE INTO products (sku, name, category_id, brand, supplier_id, cost_price, selling_price, mrp) VALUES
-- Apparel
('APP001', 'Men''s Formal Blazer (Navy)', 1, 'FormalEdge', 1, 1200, 2499, 3000),
('APP002', 'Women''s Summer Kurti (XL)', 1, 'TrendyWear', 1, 350, 799, 1000),
('APP003', 'Kids'' Denim Jeans (6-8yr)', 1, 'LittleStyle', 1, 450, 999, 1299),
('APP004', 'Men''s Cotton T-Shirts (Pack 3)', 1, 'BasicsTribe', 1, 600, 1299, 1599),
-- Footwear
('FTW001', 'Men''s Running Shoes (Size 9)', 2, 'SpeedStep', 10, 1800, 3999, 4999),
('FTW002', 'Women''s Sandals (Ethnic)', 2, 'GraceFeet', 1, 400, 899, 1199),
('FTW003', 'Kids'' School Shoes (Size 4)', 2, 'SchoolMate', 10, 550, 1199, 1499),
-- Electronics
('ELC001', 'Bluetooth Earbuds (TWS)', 3, 'SoundX', 2, 800, 1999, 2499),
('ELC002', 'USB-C Fast Charger 65W', 3, 'PowerUp', 2, 350, 899, 1199),
('ELC003', 'Smart LED Desk Lamp', 3, 'LumiTech', 2, 600, 1499, 1999),
('ELC004', 'Portable Power Bank 20000mAh', 3, 'MaxCharge', 2, 950, 2199, 2799),
-- Grocery
('GRC001', 'Organic Turmeric Powder 500g', 4, 'PureEarth', 3, 120, 249, 299),
('GRC002', 'Premium Basmati Rice 5kg', 4, 'GrainGold', 3, 380, 699, 799),
('GRC003', 'Cold-Press Coconut Oil 1L', 4, 'NaturaPress', 3, 280, 549, 649),
-- Toys
('TOY001', 'LEGO Classic Building Set', 5, 'BrickWorld', 4, 1200, 2499, 3000),
('TOY002', 'Remote Control Racing Car', 5, 'ZoomKidz', 4, 800, 1799, 2199),
('TOY003', 'Educational Science Kit (8+)', 5, 'CurioBrain', 4, 600, 1299, 1599),
-- Sports
('SPT001', 'Yoga Mat Premium 6mm', 6, 'FlexFit', 5, 500, 1099, 1399),
('SPT002', 'Cricket Bat (Full Size)', 6, 'MatchPro', 5, 1800, 3999, 4999),
('SPT003', 'Badminton Racket Set', 6, 'CourtKing', 5, 700, 1599, 1999),
-- Home & Kitchen
('HMK001', 'Non-Stick Cookware Set (5pc)', 7, 'ChefPro', 6, 1500, 3299, 3999),
('HMK002', 'Stainless Steel Water Bottle 1L', 7, 'AquaKeep', 6, 300, 699, 899),
('HMK003', 'Electric Kettle 1.7L', 7, 'BrewQuick', 6, 750, 1799, 2199),
-- Books
('BOK001', 'Python Programming Handbook', 8, 'CodePress', 7, 350, 699, 850),
('BOK002', 'Business Strategy Collection (3)', 8, 'MindBooks', 7, 900, 1799, 2199),
-- Winter
('WIN001', 'Woolen Muffler (Unisex)', 9, 'WarmWrap', 8, 250, 599, 799),
('WIN002', 'Men''s Parka Jacket (L)', 9, 'ArcticStyle', 8, 2200, 4999, 5999),
('WIN003', 'Thermal Innerwear Set', 9, 'HeatLayer', 8, 600, 1299, 1599),
-- Beauty
('BTY001', 'Vitamin C Serum 30ml', 10, 'GlowLab', 9, 320, 799, 999),
('BTY002', 'Sunscreen SPF 50 100ml', 10, 'ShieldSkin', 9, 180, 449, 599);

-- ─── Inventory (varied aging scenarios) ──────────────────────
INSERT OR IGNORE INTO inventory (product_id, quantity, location, stock_since, last_sale_date, monthly_sales) VALUES
-- Critical dead stock (>90 days, high qty)
(1,  42, 'Warehouse A', date('now','-145 days'), date('now','-30 days'), 2),
(2,  85, 'Shelf B3',    date('now','-120 days'), date('now','-45 days'), 5),
(5,  38, 'Warehouse A', date('now','-180 days'), date('now','-60 days'), 1),
(8,  67, 'Shelf A2',    date('now','-95 days'),  date('now','-20 days'), 8),
(15, 120,'Warehouse B', date('now','-200 days'), date('now','-90 days'), 3),
(21, 55, 'Warehouse A', date('now','-160 days'), date('now','-40 days'), 2),
(26, 90, 'Shelf C1',    date('now','-110 days'), date('now','-50 days'), 4),
(27, 35, 'Warehouse B', date('now','-250 days'), date('now','-120 days'),1),
-- Moderate risk (45-90 days)
(3,  22, 'Shelf D2',    date('now','-75 days'),  date('now','-10 days'), 6),
(4,  48, 'Shelf B1',    date('now','-80 days'),  date('now','-5 days'),  12),
(9,  31, 'Shelf A3',    date('now','-60 days'),  date('now','-7 days'),  15),
(16, 18, 'Shelf E1',    date('now','-65 days'),  date('now','-14 days'), 5),
(18, 40, 'Warehouse A', date('now','-55 days'),  date('now','-3 days'),  18),
(22, 25, 'Shelf D1',    date('now','-70 days'),  date('now','-12 days'), 8),
(28, 60, 'Shelf C3',    date('now','-88 days'),  date('now','-25 days'), 7),
-- Low risk / healthy (< 45 days)
(6,  15, 'Shelf B2',    date('now','-20 days'),  date('now','-2 days'),  25),
(7,  30, 'Shelf A1',    date('now','-15 days'),  date('now','-1 days'),  35),
(10, 20, 'Shelf A4',    date('now','-30 days'),  date('now','-4 days'),  20),
(11, 45, 'Warehouse A', date('now','-25 days'),  date('now','-3 days'),  30),
(12, 200,'Shelf F1',    date('now','-10 days'),  date('now','-1 days'),  80),
(13, 150,'Shelf F2',    date('now','-8 days'),   date('now','-1 days'),  60),
(14, 80, 'Shelf F3',    date('now','-12 days'),  date('now','-2 days'),  40),
(17, 15, 'Shelf E2',    date('now','-35 days'),  date('now','-5 days'),  12),
(19, 25, 'Warehouse B', date('now','-40 days'),  date('now','-8 days'),  10),
(20, 18, 'Shelf D3',    date('now','-28 days'),  date('now','-4 days'),  15),
(23, 12, 'Shelf A5',    date('now','-22 days'),  date('now','-3 days'),  22),
(24, 35, 'Shelf G1',    date('now','-18 days'),  date('now','-2 days'),  45),
(25, 28, 'Shelf G2',    date('now','-32 days'),  date('now','-6 days'),  18),
(29, 50, 'Shelf H1',    date('now','-14 days'),  date('now','-2 days'),  55),
(30, 40, 'Shelf H2',    date('now','-20 days'),  date('now','-3 days'),  38);

-- ─── Business Rules ──────────────────────────────────────────
INSERT OR IGNORE INTO business_rules (rule_name, rule_type, rule_value, priority, description) VALUES
('Dead Stock Threshold', 'aging', '60', 10, 'Products with stock age > 60 days are flagged as dead stock'),
('Critical Stock Threshold', 'aging', '90', 10, 'Products > 90 days are critical dead stock'),
('Minimum Discount Cap', 'margin', '10', 8, 'Minimum discount must be at least 10%'),
('Maximum Discount Cap', 'margin', '50', 8, 'Maximum discount cannot exceed 50% of MRP'),
('Bundle Minimum Qty', 'qty', '10', 6, 'Bundle strategy requires at least 10 units'),
('Clearance Margin Floor', 'margin', '5', 9, 'Clearance price must recover at least 5% above cost'),
('Return Window Compliance', 'aging', 'supplier_policy', 10, 'Only recommend supplier return if within return window'),
('Seasonal Clearance Trigger', 'category', 'winter:60,festive:45', 7, 'Seasonal items get lower dead stock threshold'),
('High Value Protection', 'margin', '2000', 8, 'Products with cost > 2000 get conservative discount strategy'),
('Low Stock Exclude', 'qty', '5', 9, 'Products with < 5 units skip bulk discount strategy');

-- ─── Default Settings ─────────────────────────────────────────
INSERT OR IGNORE INTO settings (key, value, label, type) VALUES
('openai_api_key', '', 'OpenAI API Key', 'password'),
('openai_model', 'gpt-4o-mini', 'OpenAI Model', 'select'),
('dead_stock_days', '60', 'Dead Stock Threshold (days)', 'number'),
('critical_days', '90', 'Critical Threshold (days)', 'number'),
('max_discount_pct', '50', 'Maximum Discount %', 'number'),
('currency_symbol', '₹', 'Currency Symbol', 'text'),
('store_name', 'My Retail Store', 'Store Name', 'text'),
('theme', 'dark', 'Default Theme', 'select');
