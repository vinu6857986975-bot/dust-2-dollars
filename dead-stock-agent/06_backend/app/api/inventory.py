# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Inventory API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import sqlite3
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_inventory(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("""
        SELECT i.*, p.sku, p.name as product_name, p.category, p.cost_price, p.selling_price,
               s.name as supplier_name, s.return_allowed, s.return_window_days,
               CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days,
               ROUND(i.quantity * p.cost_price, 2) as cost_value,
               ROUND(i.quantity * p.selling_price, 2) as retail_value,
               CASE 
                   WHEN CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) >= 120 THEN 'CRITICAL'
                   WHEN CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) >= 60 THEN 'WARNING'
                   ELSE 'HEALTHY'
               END as dead_stock_status
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        ORDER BY age_days DESC
    """).fetchall()
    return [dict(r) for r in rows]

@router.put("/{product_id}")
def update_inventory(product_id: int, quantity: int, conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("UPDATE inventory SET quantity = ? WHERE product_id = ?", (quantity, product_id))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    conn.commit()
    return {"message": "Inventory updated successfully", "product_id": product_id, "quantity": quantity}
