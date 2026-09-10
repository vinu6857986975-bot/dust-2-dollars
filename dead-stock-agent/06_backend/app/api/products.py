# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Products API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import sqlite3
from app.database import get_db
from app.schemas import ProductCreate, ProductResponse

router = APIRouter()

@router.get("/", response_model=List[dict])
def list_products(category: str = None, conn: sqlite3.Connection = Depends(get_db)):
    query = """
        SELECT p.*, s.name as supplier_name, s.return_allowed, s.return_window_days,
               i.quantity, i.stock_since, i.last_sale_date,
               CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days
        FROM products p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN inventory i ON p.id = i.product_id
    """
    params = []
    if category:
        query += " WHERE p.category = ?"
        params.append(category)
    query += " ORDER BY p.id ASC"
    
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@router.get("/{product_id}")
def get_product(product_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("""
        SELECT p.*, s.name as supplier_name, s.return_allowed, s.return_window_days,
               s.refund_type, s.restocking_fee_pct, s.exchange_allowed,
               i.quantity, i.location, i.stock_since, i.last_sale_date,
               CAST(julianday('now') - julianday(i.stock_since) AS INTEGER) as age_days
        FROM products p
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.id = ?
    """, (product_id,)).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return dict(row)

@router.post("/", status_code=201)
def create_product(product: ProductCreate, conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO products (sku, name, category, brand, description, cost_price, selling_price, supplier_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product.sku, product.name, product.category, product.brand, product.description,
              product.cost_price, product.selling_price, product.supplier_id))
        conn.commit()
        return {"id": cur.lastrowid, "message": "Product created successfully"}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
