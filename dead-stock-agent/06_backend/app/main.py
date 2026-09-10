# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Enterprise Backend Service
Modular FastAPI application orchestrating multi-agent dead-stock decision intelligence.
"""
import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import products, inventory, decisions, suppliers, dashboard

app = FastAPI(
    title="DUST 2 DOLLAR — Dead-Stock Decision API",
    description="Autonomous Multi-Agent AI Capital Recovery Platform for Retail Inventory",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(decisions.router, prefix="/api/decisions", tags=["Decisions"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "platform": "DUST 2 DOLLAR",
        "version": "2.4.0",
        "agents": ["StockAgent", "ProductAgent", "StrategyAgent", "DecisionEngine"],
        "rag_layer": "Active (Knowledge Graph + Policy Rules)",
        "security_guardrails": "Deterministic Constraint Engine Enabled"
    }

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to DUST 2 DOLLAR Autonomous Multi-Agent API",
        "docs": "/docs",
        "health": "/api/health"
    }
