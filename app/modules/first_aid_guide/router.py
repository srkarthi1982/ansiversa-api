from fastapi import APIRouter, Query, Response, status
from app.modules.first_aid_guide import service
from app.modules.first_aid_guide.dependencies import CurrentFirstAidGuideUser, FirstAidGuideDB
from app.modules.first_aid_guide.schemas import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest, DashboardResponse, GuideCreateRequest, GuideDetailResponse, GuideListResponse, GuideSort, GuideUpdateRequest, InsightsResponse

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getFirstAidGuideDashboard")
def get_dashboard(db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getFirstAidGuideInsights")
def get_insights(db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.get_insights(db, current_user)


@router.get("/categories", response_model=list[CategoryResponse], operation_id="listFirstAidGuideCategories")
def list_categories(db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.list_categories(db)


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createFirstAidGuideCategory")
def create_category(payload: CategoryCreateRequest, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.create_category(db, payload)


@router.put("/categories/{category_id}", response_model=CategoryResponse, operation_id="updateFirstAidGuideCategory")
def update_category(category_id: str, payload: CategoryUpdateRequest, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.update_category(db, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteFirstAidGuideCategory")
def delete_category(category_id: str, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    service.delete_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/guides", response_model=GuideListResponse, operation_id="listFirstAidGuides")
def list_guides(db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser, q: str | None = Query(default=None), category_id: str | None = Query(default=None, alias="categoryId"), bookmarked: bool = False, sort_by: GuideSort = Query(default="display", alias="sortBy"), page: int = Query(default=1, ge=1), page_size: int = Query(default=25, alias="pageSize", ge=1, le=100)):
    return service.list_guides(db, current_user, q, category_id, bookmarked, sort_by, page, page_size)


@router.post("/guides", response_model=GuideDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createFirstAidGuide")
def create_guide(payload: GuideCreateRequest, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.create_guide(db, payload)


@router.get("/guides/{guide_id}", response_model=GuideDetailResponse, operation_id="getFirstAidGuide")
def get_guide(guide_id: str, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.get_guide(db, current_user, guide_id)


@router.put("/guides/{guide_id}", response_model=GuideDetailResponse, operation_id="updateFirstAidGuide")
def update_guide(guide_id: str, payload: GuideUpdateRequest, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.update_guide(db, guide_id, payload)


@router.delete("/guides/{guide_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteFirstAidGuide")
def delete_guide(guide_id: str, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    service.delete_guide(db, guide_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/guides/{guide_id}/bookmark", response_model=GuideDetailResponse, operation_id="bookmarkFirstAidGuide")
def bookmark_guide(guide_id: str, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.set_bookmark(db, current_user, guide_id, True)


@router.post("/guides/{guide_id}/unbookmark", response_model=GuideDetailResponse, operation_id="unbookmarkFirstAidGuide")
def unbookmark_guide(guide_id: str, db: FirstAidGuideDB, current_user: CurrentFirstAidGuideUser):
    return service.set_bookmark(db, current_user, guide_id, False)
