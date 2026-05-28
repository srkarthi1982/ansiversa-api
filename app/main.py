from fastapi import FastAPI
from app.modules.health.routes import router as health_router

app = FastAPI(
    title="Ansiversa API",
    description="Single source of truth API for the Ansiversa ecosystem.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])


@app.get("/")
def root():
    return {
        "name": "Ansiversa API",
        "status": "running",
        "version": "0.1.0",
    }
