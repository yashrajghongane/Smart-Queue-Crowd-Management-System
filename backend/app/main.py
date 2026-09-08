from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {"status": "ok"}
