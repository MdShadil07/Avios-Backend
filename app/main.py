
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.complaints import router as complaints_router
from app.db.database import Base, engine
from app.models.audit import AuditLog
from app.models.complaint import Complaint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.

    Creates all SQLAlchemy tables when the application starts.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AIVOA QMS API",
    description="AI-Powered Customer Complaint Management System",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(complaints_router)
app.include_router(analysis_router)


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AIVOA QMS API",
    }

