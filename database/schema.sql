-- Construct-AI Database Schema
-- Compatible with PostgreSQL and SQLite

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'Civil Engineer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    project_name VARCHAR(200) NOT NULL,
    building_type VARCHAR(100) DEFAULT 'residential',
    plot_area FLOAT DEFAULT 3000.0,
    floor_area FLOAT NOT NULL,
    floors INTEGER DEFAULT 1,
    location VARCHAR(255) DEFAULT 'Bangalore, India',
    status VARCHAR(50) DEFAULT 'In Progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS buildings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    plot_area FLOAT,
    built_up_area FLOAT,
    floors INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    file_path TEXT,
    image_type VARCHAR(50) DEFAULT 'floor_plan',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS building_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    rooms INTEGER,
    doors INTEGER,
    windows INTEGER,
    estimated_floor_area FLOAT,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS suppliers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(30),
    address TEXT,
    distance_km FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    rating FLOAT DEFAULT 4.5
);

CREATE TABLE IF NOT EXISTS material_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id VARCHAR(50) REFERENCES materials(id),
    supplier_id VARCHAR(50) REFERENCES suppliers(id),
    price FLOAT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS supplier_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id VARCHAR(50) REFERENCES suppliers(id),
    material_id VARCHAR(50) REFERENCES materials(id),
    stock_status VARCHAR(50) DEFAULT 'in_stock',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    supplier_id VARCHAR(50) REFERENCES suppliers(id),
    total_cost FLOAT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS procurement_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    phase VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'proposed',
    approved_by INTEGER REFERENCES users(id),
    signature_data TEXT,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS delivery_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    procurement_order_id INTEGER REFERENCES procurement_orders(id),
    batch_name VARCHAR(100) NOT NULL,
    materials TEXT,
    scheduled_date DATE,
    vehicle_type VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id),
    agent_name VARCHAR(100) NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    status VARCHAR(50) DEFAULT 'done',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for rapid lookup
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_proj ON agent_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_mat_prices_mat ON material_prices(material_id);
CREATE INDEX IF NOT EXISTS idx_mat_prices_sup ON material_prices(supplier_id);
