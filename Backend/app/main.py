from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, resources, recommendations, accounts, anomalies, phase_a
from app.models.database import Base, engine
from app.models import user  # ensures User model is registered

app = FastAPI(
    title="Cloud Cost Optimizer API",
    description="AWS cost optimization assistant — local Postgres + JWT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables at startup (only in development/when needed)
import os
if os.getenv("APP_ENV") != "production":
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router,            prefix="/api/auth",            tags=["Auth"])
app.include_router(accounts.router,        prefix="/api/accounts",        tags=["Accounts"])
app.include_router(resources.router,       prefix="/api/resources",       tags=["Resources"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(anomalies.router,       prefix="/api/anomalies",       tags=["Anomalies"])
app.include_router(phase_a.router,         prefix="/api/phase_a",         tags=["Phase A ML"])

@app.get("/")
def health():
    return {"status": "ok"}

# Vercel serverless handler
from mangum import Mangum

handler = Mangum(app)
