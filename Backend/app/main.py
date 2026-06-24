from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from app.routes import auth, resources, recommendations, accounts
from app.routes import auth, resources, recommendations, accounts, chat
=======
from app.routes import auth, resources, recommendations, accounts, anomalies, phase_a
>>>>>>> 922b580a6d45d3a25797d6e2a9dd655eacbf6e28

app = FastAPI(
    title="Cloud Cost Optimizer API",
    description="AWS cost optimization assistant — local SQLite + JWT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,            prefix="/api/auth",            tags=["Auth"])
app.include_router(accounts.router,        prefix="/api/accounts",        tags=["Accounts"])
app.include_router(resources.router,       prefix="/api/resources",       tags=["Resources"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
<<<<<<< HEAD
app.include_router(chat.router,            prefix="/api/chat",            tags=["RAG Chat"])
=======
app.include_router(anomalies.router,       prefix="/api/anomalies",       tags=["Anomalies"])
app.include_router(phase_a.router,         prefix="/api/phase_a",         tags=["Phase A ML"])

>>>>>>> 922b580a6d45d3a25797d6e2a9dd655eacbf6e28

@app.get("/")
def health():
    return {"status": "ok"}





  