# -*- coding: utf-8 -*-
"""
Deterministic Composite Capital Recovery Scoring Engine
"""
def score_action(action: str, stock_age: int, margin_pct: float, qty: int, return_allowed: bool, return_window: int) -> float:
    score = 50.0
    if action == 'DISCOUNT':
        score += min(30.0, margin_pct * 0.5) + (stock_age / 10.0)
    elif action == 'RETURN_SUPPLIER':
        if return_allowed and stock_age <= return_window:
            score = 92.0 - (stock_age / return_window) * 20.0
        else:
            score = 0.0  # Hard constraint failure
    elif action == 'BUNDLE':
        score += 20.0 if qty >= 10 else -10.0
        score += min(15.0, margin_pct * 0.3)
    elif action == 'CLEARANCE':
        score += (stock_age / 5.0) if stock_age > 150 else 10.0
    return round(max(0.0, min(100.0, score)), 1)
