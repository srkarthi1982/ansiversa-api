from fastapi import APIRouter
from .schemas import AboutResponse
from .service import get_about_content

router = APIRouter(prefix="/content", tags=["content"])

@router.get("/about", response_model=AboutResponse)
async def about():
    return get_about_content()