-- ============================================================
-- DUST 2 DOLLAR — Business Dead-Stock Decision Agent
-- Database Schema
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ─── Suppliers ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS suppliers (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    contact_email       TEXT,
    contact_phone       TEXT,
    return_allowed      INTEGER DEFAULT 0,        -- 0=No, 1=Yes
    return_window_days  INTEGER DEFAULT 0,
    refund_type         TEXT DEFAULT 'none',      -- none/full/partial/credit
    exchange_allowed    INTEGER DEFAULT 0,
    min_return_qty      INTEGER DEFAULT 1,
    penalty_pct         REAL DEFAULT 0.0,
    notes               TEXT,
    created_at          TEXT DEFAULT (datetime('now'))
);

-- ─── Categories ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    seasonality     TEXT DEFAULT 'none',  -- none/summer/winter/festive/monsoon
    avg_shelf_days  INTEGER DEFAULT 90,
    dead_threshold_days INTEGER DEFAULT 60
);

-- ─── Products ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,
    category_id     INTEGER REFERENCES categories(id),
    brand           TEXT,
    supplier_id     INTEGER REFERENCES suppliers(id),
    cost_price      REAL NOT NULL DEFAULT 0,
    selling_price   REAL NOT NULL DEFAULT 0,
    mrp             REAL,
    unit            TEXT DEFAULT 'pcs',
    image_url       TEXT,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ─── Inventory ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id),
    quantity        INTEGER NOT NULL DEFAULT 0,
    location        TEXT DEFAULT 'Warehouse A',
    stock_since     TEXT NOT NULL,
    last_sale_date  TEXT,
    monthly_sales   REAL DEFAULT 0,
    reorder_level   INTEGER DEFAULT 10,
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ─── Business Rules ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS business_rules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name   TEXT NOT NULL,
    rule_type   TEXT NOT NULL,   -- aging/margin/qty/category
    rule_value  TEXT NOT NULL,
    priority    INTEGER DEFAULT 5,
    enabled     INTEGER DEFAULT 1,
    description TEXT
);

-- ─── Decisions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS decisions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id          INTEGER NOT NULL REFERENCES products(id),
    analysis_input      TEXT,   -- JSON snapshot of input
    recommended_action  TEXT NOT NULL,
    action_score        REAL,
    confidence          TEXT DEFAULT 'Medium',  -- Low/Medium/High
    reasoning           TEXT,
    alternatives        TEXT,   -- JSON array
    risk_level          TEXT DEFAULT 'Medium',
    estimated_recovery  REAL DEFAULT 0,
    agent_trace         TEXT,   -- JSON trace of all agents
    created_at          TEXT DEFAULT (datetime('now')),
    user_decision       TEXT DEFAULT 'pending',  -- pending/approved/rejected
    user_notes          TEXT,
    decided_at          TEXT
);

-- ─── Agent Logs ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER REFERENCES decisions(id),
    agent_name  TEXT NOT NULL,
    step_index  INTEGER DEFAULT 0,
    input_data  TEXT,
    output_data TEXT,
    duration_ms INTEGER DEFAULT 0,
    status      TEXT DEFAULT 'ok',  -- ok/error/skipped
    created_at  TEXT DEFAULT (datetime('now'))
);

-- ─── Settings ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT,
    label       TEXT,
    type        TEXT DEFAULT 'text',  -- text/number/bool/select
    updated_at  TEXT DEFAULT (datetime('now'))
);
