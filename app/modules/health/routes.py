from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import check_parent_database

router = APIRouter()


@router.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "ansiversa-api",
    }


@router.get("/db/")
def database_health_check() -> dict[str, str]:
    try:
        check_parent_database()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Parent database is unavailable.",
        ) from exc

    return {
        "status": "ok",
        "database": "parent",
    }
