from fastapi import APIRouter, Query, Response, status

from app.modules.home_maintenance_planner import service
from app.modules.home_maintenance_planner.dependencies import CurrentHomeMaintenanceUser, HomeMaintenanceDB
from app.modules.home_maintenance_planner.schemas import (
    ArchiveFilter,
    CompletionRequest,
    DashboardResponse,
    InsightsResponse,
    MaintenanceLookupCreateRequest,
    MaintenanceLookupResponse,
    MaintenanceLookupUpdateRequest,
    MaintenanceTaskCreateRequest,
    MaintenanceTaskDetailResponse,
    MaintenanceTaskSummaryResponse,
    MaintenanceTaskUpdateRequest,
    TaskSort,
    TaskTimeFilter,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getHomeMaintenancePlannerDashboard")
def get_dashboard(db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getHomeMaintenancePlannerInsights")
def get_insights(db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.get_insights(db, current_user)


@router.get("/areas", response_model=list[MaintenanceLookupResponse], operation_id="listHomeMaintenancePlannerAreas")
def list_areas(db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.list_areas(db, current_user)


@router.post("/areas", response_model=MaintenanceLookupResponse, status_code=status.HTTP_201_CREATED, operation_id="createHomeMaintenancePlannerArea")
def create_area(payload: MaintenanceLookupCreateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.create_area(db, current_user, payload)


@router.put("/areas/{area_id}", response_model=MaintenanceLookupResponse, operation_id="updateHomeMaintenancePlannerArea")
def update_area(area_id: str, payload: MaintenanceLookupUpdateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.update_area(db, current_user, area_id, payload)


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHomeMaintenancePlannerArea")
def delete_area(area_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    service.delete_area(db, current_user, area_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=list[MaintenanceLookupResponse], operation_id="listHomeMaintenancePlannerCategories")
def list_categories(db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=MaintenanceLookupResponse, status_code=status.HTTP_201_CREATED, operation_id="createHomeMaintenancePlannerCategory")
def create_category(payload: MaintenanceLookupCreateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.create_category(db, current_user, payload)


@router.put("/categories/{category_id}", response_model=MaintenanceLookupResponse, operation_id="updateHomeMaintenancePlannerCategory")
def update_category(category_id: str, payload: MaintenanceLookupUpdateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHomeMaintenancePlannerCategory")
def delete_category(category_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tasks", response_model=list[MaintenanceTaskSummaryResponse], operation_id="listHomeMaintenancePlannerTasks")
def list_tasks(
    db: HomeMaintenanceDB,
    current_user: CurrentHomeMaintenanceUser,
    q: str | None = Query(default=None),
    archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"),
    area_id: str | None = Query(default=None, alias="areaId"),
    category_id: str | None = Query(default=None, alias="categoryId"),
    priority: str | None = Query(default=None),
    time_filter: TaskTimeFilter = Query(default="all", alias="timeFilter"),
    sort_by: TaskSort = Query(default="due", alias="sortBy"),
):
    return service.list_tasks(db, current_user, q, archive_filter, area_id, category_id, priority, time_filter, sort_by)


@router.post("/tasks", response_model=MaintenanceTaskDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createHomeMaintenancePlannerTask")
def create_task(payload: MaintenanceTaskCreateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.create_task(db, current_user, payload)


@router.get("/tasks/{task_id}", response_model=MaintenanceTaskDetailResponse, operation_id="getHomeMaintenancePlannerTask")
def get_task(task_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.get_task(db, current_user, task_id)


@router.put("/tasks/{task_id}", response_model=MaintenanceTaskDetailResponse, operation_id="updateHomeMaintenancePlannerTask")
def update_task(task_id: str, payload: MaintenanceTaskUpdateRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.update_task(db, current_user, task_id, payload)


@router.post("/tasks/{task_id}/complete", response_model=MaintenanceTaskDetailResponse, operation_id="completeHomeMaintenancePlannerTask")
def complete_task(task_id: str, payload: CompletionRequest, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.complete_task(db, current_user, task_id, payload)


@router.post("/tasks/{task_id}/reopen", response_model=MaintenanceTaskDetailResponse, operation_id="reopenHomeMaintenancePlannerTask")
def reopen_task(task_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.reopen_task(db, current_user, task_id)


@router.post("/tasks/{task_id}/archive", response_model=MaintenanceTaskDetailResponse, operation_id="archiveHomeMaintenancePlannerTask")
def archive_task(task_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.set_task_archived(db, current_user, task_id, True)


@router.post("/tasks/{task_id}/restore", response_model=MaintenanceTaskDetailResponse, operation_id="restoreHomeMaintenancePlannerTask")
def restore_task(task_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    return service.set_task_archived(db, current_user, task_id, False)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHomeMaintenancePlannerTask")
def delete_task(task_id: str, db: HomeMaintenanceDB, current_user: CurrentHomeMaintenanceUser):
    service.delete_task(db, current_user, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

