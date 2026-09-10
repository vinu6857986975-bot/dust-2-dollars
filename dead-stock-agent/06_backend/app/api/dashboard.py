# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Dashboard API Router
"""
from fastapi import APIRouter, Depends
import sqlite3
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_dashboard_metrics(conn: sqlite3.Connection = Depends(get_db)):
    # Total dead-stock value
    total_val = conn.execute("""
        SELECT SUM(i.quantity * p.cost_price) as total_dead_stock_cost,
               SUM(i.quantity * p.selling_price) as total_dead_stock_retail,
               COUNT(DISTINCT p.id) as total_products,
               SUM(i.quantity) as total_units
        FROM inventory i
        JOIN products p ON i.product_id = p.id
    """).fetchone()

    # Critical products count (age >= 120 days)
    critical = conn.execute("""
        SELECT COUNT(*) as critical_count,
               COALESCE(SUM(i.quantity * p.cost_price), 0) as critical_value
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE (julianday('now') - julianday(i.stock_since)) >= 120
    """).fetchone()

    # Recovery potential from decisions
    recovery = conn.execute("""
        SELECT COALESCE(SUM(expected_recovery), 0) as total_projected_recovery,
               COUNT(*) as decisions_count
        FROM decisions
    """).fetchone()

    # Recent decisions
    recent_decisions = conn.execute("""
        SELECT d.*, p.name as product_name, p.sku
        FROM decisions d
        JOIN products p ON d.product_id = p.id
        ORDER BY d.id DESC LIMIT 5
    """).fetchall()

    return {
        "dead_stock_cost_value": total_val["total_dead_stock_cost"] or 0,
        "dead_stock_retail_value": total_val["total_dead_stock_retail"] or 0,
        "total_sku_count": total_val["total_products"] or 0,
        "total_units": total_val["total_units"] or 0,
        "critical_count": critical["critical_count"] or 0,
        "critical_value": critical["critical_value"] or 0,
        "projected_recovery_value": recovery["total_projected_recovery"] or 0,
        "recovery_rate_pct": round((recovery["total_projected_recovery"] / (total_val["total_dead_stock_cost"] or 1)) * 100, 1),
        "recent_decisions": [dict(r) for r in recent_decisions]
    }
