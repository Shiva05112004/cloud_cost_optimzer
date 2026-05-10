from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── Auth ────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Cloud Account ───────────────────────────────────────
class ConnectAccountRequest(BaseModel):
    account_name: str
    role_arn: str


class AccountOut(BaseModel):
    id: int
    account_name: str
    provider: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── EC2 / Resources ─────────────────────────────────────
class EC2InstanceOut(BaseModel):
    instance_id: str
    instance_type: str
    state: str
    avg_cpu: float
    region: str
    launch_time: str


# ─── Cost ────────────────────────────────────────────────
class CostSummaryOut(BaseModel):
    total_usd: float
    by_service: dict
    period: str


# ─── ML / Recommendations ────────────────────────────────
class RecommendationOut(BaseModel):
    instance_id: str
    issue: str
    action: str
    current_cost: float
    estimated_savings: float
    recommended_type: Optional[str]
    confidence: float
    risk: str
    priority_score: float


class RecommendationListOut(BaseModel):
    count: int
    total_potential_savings: float
    recommendations: List[RecommendationOut]


# ─── Alerts ──────────────────────────────────────────────
class AlertRequest(BaseModel):
    to_email: str
    resource_id: str
    savings: float


class AlertResponse(BaseModel):
    message_id: str
    status: str
    to: str


# ─── Anomaly ─────────────────────────────────────────────
class AnomalyResult(BaseModel):
    is_anomaly: bool
    z_score: float
    current: float
    mean: float
    message: str


# ─── Forecast ────────────────────────────────────────────
class ForecastResult(BaseModel):
    slope: float
    intercept: float
    forecast: List[float]
    trend: strutils 