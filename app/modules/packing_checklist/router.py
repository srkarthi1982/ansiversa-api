from fastapi import APIRouter, Query, Response, status

from app.modules.packing_checklist import service
from app.modules.packing_checklist.dependencies import CurrentPackingChecklistUser, PackingChecklistDB
from app.modules.packing_checklist.schemas import (
    ArchiveFilter,
    ChecklistSort,
    PackedFilter,
    PackingCategoryCreateRequest,
    PackingCategoryResponse,
    PackingCategoryUpdateRequest,
    PackingChecklistCreateRequest,
    PackingChecklistDashboardResponse,
    PackingChecklistDetailResponse,
    PackingChecklistInsightsResponse,
    PackingChecklistSummaryResponse,
    PackingChecklistUpdateRequest,
    PackingItemCreateRequest,
    PackingItemResponse,
    PackingItemUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=PackingChecklistDashboardResponse, operation_id="getPackingChecklistDashboard")
def get_dashboard(db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=PackingChecklistInsightsResponse, operation_id="getPackingChecklistInsights")
def get_insights(db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.get_insights(db, current_user)


@router.get("/categories", response_model=list[PackingCategoryResponse], operation_id="listPackingChecklistCategories")
def list_categories(db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=PackingCategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createPackingChecklistCategory")
def create_category(payload: PackingCategoryCreateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=PackingCategoryResponse, operation_id="updatePackingChecklistCategory")
def update_category(category_id: str, payload: PackingCategoryUpdateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deletePackingChecklistCategory")
def delete_category(category_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/checklists", response_model=list[PackingChecklistSummaryResponse], operation_id="listPackingChecklists")
def list_checklists(
    db: PackingChecklistDB,
    current_user: CurrentPackingChecklistUser,
    q: str | None = Query(default=None),
    archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"),
    trip_type: str | None = Query(default=None, alias="tripType"),
    sort_by: ChecklistSort = Query(default="updated", alias="sortBy"),
):
    return service.list_checklists(db, current_user, q, archive_filter, trip_type, sort_by)


@router.post("/checklists", response_model=PackingChecklistDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createPackingChecklist")
def create_checklist(payload: PackingChecklistCreateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.create_checklist(db, current_user, payload)


@router.get("/checklists/{checklist_id}", response_model=PackingChecklistDetailResponse, operation_id="getPackingChecklist")
def get_checklist(checklist_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.get_checklist(db, current_user, checklist_id)


@router.put("/checklists/{checklist_id}", response_model=PackingChecklistDetailResponse, operation_id="updatePackingChecklist")
def update_checklist(checklist_id: str, payload: PackingChecklistUpdateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.update_checklist(db, current_user, checklist_id, payload)


@router.post("/checklists/{checklist_id}/duplicate", response_model=PackingChecklistDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicatePackingChecklist")
def duplicate_checklist(checklist_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.duplicate_checklist(db, current_user, checklist_id)


@router.post("/checklists/{checklist_id}/archive", response_model=PackingChecklistDetailResponse, operation_id="archivePackingChecklist")
def archive_checklist(checklist_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.set_checklist_archived(db, current_user, checklist_id, True)


@router.post("/checklists/{checklist_id}/restore", response_model=PackingChecklistDetailResponse, operation_id="restorePackingChecklist")
def restore_checklist(checklist_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.set_checklist_archived(db, current_user, checklist_id, False)


@router.delete("/checklists/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deletePackingChecklist")
def delete_checklist(checklist_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    service.delete_checklist(db, current_user, checklist_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/checklists/{checklist_id}/items", response_model=PackingItemResponse, status_code=status.HTTP_201_CREATED, operation_id="createPackingChecklistItem")
def create_item(checklist_id: str, payload: PackingItemCreateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.create_item(db, current_user, checklist_id, payload)


@router.get("/checklists/{checklist_id}/items", response_model=list[PackingItemResponse], operation_id="listPackingChecklistItems")
def list_items(
    checklist_id: str,
    db: PackingChecklistDB,
    current_user: CurrentPackingChecklistUser,
    category_id: str | None = Query(default=None, alias="categoryId"),
    packed_filter: PackedFilter = Query(default="all", alias="packedFilter"),
):
    return service.list_items(db, current_user, checklist_id, category_id, packed_filter)


@router.put("/items/{item_id}", response_model=PackingItemResponse, operation_id="updatePackingChecklistItem")
def update_item(item_id: str, payload: PackingItemUpdateRequest, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.update_item(db, current_user, item_id, payload)


@router.post("/items/{item_id}/packed", response_model=PackingItemResponse, operation_id="packPackingChecklistItem")
def pack_item(item_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.set_item_packed(db, current_user, item_id, True)


@router.post("/items/{item_id}/unpacked", response_model=PackingItemResponse, operation_id="unpackPackingChecklistItem")
def unpack_item(item_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    return service.set_item_packed(db, current_user, item_id, False)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deletePackingChecklistItem")
def delete_item(item_id: str, db: PackingChecklistDB, current_user: CurrentPackingChecklistUser):
    service.delete_item(db, current_user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
