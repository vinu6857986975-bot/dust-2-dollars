# -*- coding: utf-8 -*-
"""
DUST 2 DOLLAR — Pydantic Schemas for Validation & API Contracts
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    sku: str = Field(..., example="JKT-WIN-001")
    name: str = Field(..., example="Arctic Insulated Winter Jacket")
    category: str = Field(..., example="Apparel")
    brand: Optional[str] = Field(None, example="NorthPeak")
    description: Optional[str] = None
    cost_price: float = Field(..., gt=0, example=1500.0)
    selling_price: float = Field(..., gt=0, example=2499.0)
    supplier_id: int = Field(..., example=1)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[str] = None

    class Config:
        orm_mode = True

class InventoryBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=0, example=42)
    location: str = Field(default="Warehouse A", example="Warehouse A")
    stock_since: str = Field(..., example="2025-10-15")
    last_sale_date: Optional[str] = Field(None, example="2025-11-01")

class InventoryResponse(InventoryBase):
    id: int
    age_days: Optional[int] = None
    status: Optional[str] = None
    cost_value: Optional[float] = None
    retail_value: Optional[float] = None

class SupplierBase(BaseModel):
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    return_allowed: int = 1
    return_window_days: int = 30
    refund_type: str = "credit"
    restocking_fee_pct: float = 10.0
    exchange_allowed: int = 1

class SupplierResponse(SupplierBase):
    id: int

class AnalyzeRequest(BaseModel):
    product_id: int = Field(..., example=1)
    force_refresh: bool = False
    custom_constraints: Optional[Dict[str, Any]] = None

class ActionItem(BaseModel):
    action: str
    feasibility: str
    score: float
    expected_recovery: float
    description: str
    risk_level: str

class DecisionResponse(BaseModel):
    decision_id: Optional[int] = None
    product_id: int
    sku: str
    product_name: str
    age_days: int
    stock_qty: int
    cost_value: float
    recommended_action: str
    confidence: float
    reasoning: str
    expected_recovery_pct: float
    expected_recovery_amount: float
    actions_ranked: List[ActionItem]
    agent_logs: List[str]
    guardrail_check: str = "PASSED"

class DecisionApproval(BaseModel):
    notes: Optional[str] = None
