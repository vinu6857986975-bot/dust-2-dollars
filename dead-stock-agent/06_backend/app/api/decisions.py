# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Decisions API Router
Orchestrates multi-agent analysis and manages approval workflows.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import sqlite3
import json
from app.database import get_db
from app.schemas import AnalyzeRequest, DecisionResponse, DecisionApproval
from app.agents.orchestrator import DeadStockOrchestrator

router = APIRouter()
orchestrator = DeadStockOrchestrator()

@router.get("/")
def list_decisions(status: Optional[str] = None, conn: sqlite3.Connection = Depends(get_db)):
    query = """
        SELECT d.*, p.name as product_name, p.sku, p.cost_price, p.selling_price
        FROM decisions d
        JOIN products p ON d.product_id = p.id
    """
    params = []
    if status:
        query += " WHERE d.user_decision = ?"
        params.append(status)
    query += " ORDER BY d.id DESC LIMIT 50"
    
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@router.get("/{decision_id}")
def get_decision(decision_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("""
        SELECT d.*, p.name as product_name, p.sku, p.category, p.cost_price, p.selling_price
        FROM decisions d
        JOIN products p ON d.product_id = p.id
        WHERE d.id = ?
    """, (decision_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Decision not found")
    res = dict(row)
    if res.get("alternatives"):
        try:
            res["alternatives"] = json.loads(res["alternatives"])
        except Exception:
            pass
    return res

@router.post("/analyze")
def run_analysis(req: AnalyzeRequest, conn: sqlite3.Connection = Depends(get_db)):
    # Retrieve product, inventory, supplier, and category
    prod_row = conn.execute("SELECT * FROM products WHERE id=?", (req.product_id,)).fetchone()
    if not prod_row:
        raise HTTPException(status_code=404, detail=f"Product {req.product_id} not found")
    product = dict(prod_row)

    inv_row = conn.execute("SELECT * FROM inventory WHERE product_id=?", (req.product_id,)).fetchone()
    inventory = dict(inv_row) if inv_row else {}

    sup_row = conn.execute("SELECT * FROM suppliers WHERE id=?", (product.get("supplier_id", 1),)).fetchone()
    supplier = dict(sup_row) if sup_row else {}

    cat_row = conn.execute("SELECT * FROM categories WHERE name=?", (product.get("category", ""),)).fetchone()
    category = dict(cat_row) if cat_row else {}

    rules_rows = conn.execute("SELECT * FROM business_rules WHERE enabled=1 ORDER BY priority DESC").fetchall()
    rules = [dict(r) for r in rules_rows]

    # Run multi-agent cognitive pipeline
    decision_result = orchestrator.run(
        product=product,
        inventory=inventory,
        supplier=supplier,
        category=category,
        rules=rules
    )

    # Persist in SQLite
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO decisions (product_id, recommended_action, confidence, reasoning, alternatives, expected_recovery, user_decision)
        VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
    """, (
        req.product_id,
        decision_result.get("recommended_action", "DISCOUNT_20"),
        decision_result.get("confidence", 0.85),
        decision_result.get("reasoning", ""),
        json.dumps(decision_result.get("actions_ranked", [])),
        decision_result.get("expected_recovery_amount", 0.0)
    ))
    conn.commit()
    decision_id = cur.lastrowid
    decision_result["decision_id"] = decision_id

    return decision_result

@router.post("/{decision_id}/approve")
def approve_decision(decision_id: int, approval: DecisionApproval = None, conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("UPDATE decisions SET user_decision = 'APPROVED' WHERE id = ?", (decision_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Decision not found")
    conn.commit()
    return {"message": "Decision approved successfully", "decision_id": decision_id, "status": "APPROVED"}

@router.post("/{decision_id}/reject")
def reject_decision(decision_id: int, approval: DecisionApproval = None, conn: sqlite3.Connection = Depends(get_db)):
    cur = conn.cursor()
    cur.execute("UPDATE decisions SET user_decision = 'REJECTED' WHERE id = ?", (decision_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Decision not found")
    conn.commit()
    return {"message": "Decision rejected", "decision_id": decision_id, "status": "REJECTED"}
