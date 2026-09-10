"""
Pydantic Schemas for Request/Response Validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class ProjectCreate(BaseModel):
    project_name: str
    building_type: str = "residential"
    floor_area: float
    plot_area: Optional[float] = 3000.0
    floors: Optional[int] = 1
    location: Optional[str] = "Indiranagar, Bangalore"

class AnalysisRequest(BaseModel):
    project_id: int
    preset: Optional[str] = "villa"
    manual_override: Optional[Dict[str, Any]] = None
    supplier_weights: Optional[Dict[str, float]] = None

class ProcurementApprove(BaseModel):
    project_id: int
    engineer_name: str
    phases: Optional[List[str]] = ["Phase 1 - Foundation"]
    signature: Optional[str] = "SIG_VERIFIED"
