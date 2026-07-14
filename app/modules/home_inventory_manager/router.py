from fastapi import APIRouter, Query, Response, status

from app.modules.home_inventory_manager import service
from app.modules.home_inventory_manager.dependencies import CurrentHomeInventoryManagerUser, HomeInventoryManagerDB
from app.modules.home_inventory_manager.schemas import (
    ArchiveFilter,
    InventoryCategoryCreateRequest,
    InventoryCategoryResponse,
    InventoryCategoryUpdateRequest,
    InventoryDashboardResponse,
    InventoryInsightsResponse,
    InventoryItemCreateRequest,
    InventoryItemDetailResponse,
    InventoryItemSummaryResponse,
    InventoryItemUpdateRequest,
    ItemSort,
    WarrantyFilter,
)

router = APIRouter()


@router.get("/dashboard", response_model=InventoryDashboardResponse, operation_id="getHomeInventoryManagerDashboard")
def get_dashboard(db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InventoryInsightsResponse, operation_id="getHomeInventoryManagerInsights")
def get_insights(db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.get_insights(db, current_user)


@router.get("/categories", response_model=list[InventoryCategoryResponse], operation_id="listHomeInventoryManagerCategories")
def list_categories(db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=InventoryCategoryResponse, status_code=status.HTTP_201_CREATED, operation_id="createHomeInventoryManagerCategory")
def create_category(payload: InventoryCategoryCreateRequest, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=InventoryCategoryResponse, operation_id="updateHomeInventoryManagerCategory")
def update_category(category_id: str, payload: InventoryCategoryUpdateRequest, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHomeInventoryManagerCategory")
def delete_category(category_id: str, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/items", response_model=list[InventoryItemSummaryResponse], operation_id="listHomeInventoryManagerItems")
def list_items(
    db: HomeInventoryManagerDB,
    current_user: CurrentHomeInventoryManagerUser,
    q: str | None = Query(default=None),
    category_id: str | None = Query(default=None, alias="categoryId"),
    room: str | None = Query(default=None),
    condition: str | None = Query(default=None),
    warranty_filter: WarrantyFilter = Query(default="all", alias="warrantyFilter"),
    archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"),
    sort_by: ItemSort = Query(default="purchaseDate", alias="sortBy"),
):
    return service.list_items(db, current_user, q, category_id, room, condition, warranty_filter, archive_filter, sort_by)


@router.post("/items", response_model=InventoryItemDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createHomeInventoryManagerItem")
def create_item(payload: InventoryItemCreateRequest, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.create_item(db, current_user, payload)


@router.get("/items/{item_id}", response_model=InventoryItemDetailResponse, operation_id="getHomeInventoryManagerItem")
def get_item(item_id: str, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.get_item(db, current_user, item_id)


@router.put("/items/{item_id}", response_model=InventoryItemDetailResponse, operation_id="updateHomeInventoryManagerItem")
def update_item(item_id: str, payload: InventoryItemUpdateRequest, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.update_item(db, current_user, item_id, payload)


@router.post("/items/{item_id}/archive", response_model=InventoryItemDetailResponse, operation_id="archiveHomeInventoryManagerItem")
def archive_item(item_id: str, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.set_item_archived(db, current_user, item_id, True)


@router.post("/items/{item_id}/restore", response_model=InventoryItemDetailResponse, operation_id="restoreHomeInventoryManagerItem")
def restore_item(item_id: str, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    return service.set_item_archived(db, current_user, item_id, False)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHomeInventoryManagerItem")
def delete_item(item_id: str, db: HomeInventoryManagerDB, current_user: CurrentHomeInventoryManagerUser):
    service.delete_item(db, current_user, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
