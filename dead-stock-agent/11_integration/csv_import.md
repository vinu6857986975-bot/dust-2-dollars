# CSV & POS Import Specification
Expected CSV columns:
`sku,name,category,brand,cost_price,selling_price,quantity,stock_since,supplier_name`
Auto-parses and inserts into SQLite tables with conflict resolution on duplicate SKUs.
