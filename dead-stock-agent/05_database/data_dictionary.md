# Data Dictionary: AnyPortal Schema

## Table: `products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | Unique product ID |
| sku | TEXT | UNIQUE, NOT NULL | Stock Keeping Unit code |
| name | TEXT | NOT NULL | Product commercial name |
| category | TEXT | NOT NULL | Retail department classification |
| brand | TEXT | DEFAULT 'Generic' | Brand or manufacturer name |
| cost_price | REAL | NOT NULL | Procurement unit cost |
| selling_price | REAL | NOT NULL | Standard retail list price |
| supplier_id | INTEGER | FK -> suppliers.id | Associated supplier identifier |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

## Table: `inventory`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | Inventory record ID |
| product_id | INTEGER | FK -> products.id | Linked product |
| quantity | INTEGER | NOT NULL | Units currently on hand |
| location | TEXT | DEFAULT 'Main Warehouse' | Storage facility or store shelf |
| stock_since | DATE | NOT NULL | Date inventory was received |
| last_sale_date | DATE | NULLABLE | Date of last recorded transaction |

## Table: `suppliers`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | Supplier ID |
| name | TEXT | NOT NULL | Supplier company name |
| return_allowed | INTEGER | BOOLEAN (0/1) | Contractual return permission |
| return_window_days | INTEGER | NOT NULL | Maximum days eligible for return |
| restocking_fee_pct | REAL | DEFAULT 0.0 | Restocking penalty % |

## Table: `decisions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK, AUTOINCREMENT | Decision audit ID |
| product_id | INTEGER | FK -> products.id | Subject product |
| recommended_action | TEXT | NOT NULL | Winning strategy code |
| confidence | REAL | NOT NULL | Composite confidence score (0-100) |
| reasoning | TEXT | NOT NULL | Natural-language explanation |
| status | TEXT | DEFAULT 'pending' | 'pending', 'approved', 'rejected' |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Audit log timestamp |
