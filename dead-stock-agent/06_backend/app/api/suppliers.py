# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Suppliers API Router
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import sqlite3
from app.database import get_db

router = APIRouter()

@router.get("/")
def list_suppliers(conn: sqlite3.Connection = Depends(get_db)):
    rows = conn.execute("SELECT * FROM suppliers ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]

@router.get("/{supplier_id}")
def get_supplier(supplier_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return dict(row)
