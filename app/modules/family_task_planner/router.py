from fastapi import APIRouter, Response, status

from app.modules.family_task_planner import service
from app.modules.family_task_planner.dependencies import CurrentFamilyTaskPlannerUser, FamilyTaskPlannerDB
from app.modules.family_task_planner.schemas import (
    CategoryCreateRequest,
    CategoryDetailResponse,
    CategorySummaryResponse,
    CategoryUpdateRequest,
    FamilyTaskPlannerDashboardResponse,
    MemberCreateRequest,
    MemberDetailResponse,
    MemberSummaryResponse,
    MemberUpdateRequest,
    TaskCreateRequest,
    TaskDetailResponse,
    TaskDuplicateRequest,
    TaskSummaryResponse,
    TaskUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=FamilyTaskPlannerDashboardResponse)
def get_dashboard(db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.get_dashboard(db, current_user)


@router.get("/tasks", response_model=list[TaskSummaryResponse])
def list_tasks(db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.list_tasks(db, current_user)


@router.post("/tasks", response_model=TaskDetailResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.create_task(db, current_user, payload)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.get_task(db, current_user, task_id)


@router.put("/tasks/{task_id}", response_model=TaskDetailResponse)
def update_task(task_id: str, payload: TaskUpdateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.update_task(db, current_user, task_id, payload)


@router.post("/tasks/{task_id}/complete", response_model=TaskDetailResponse)
def complete_task(task_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.complete_task(db, current_user, task_id)


@router.post("/tasks/{task_id}/reopen", response_model=TaskDetailResponse)
def reopen_task(task_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.reopen_task(db, current_user, task_id)


@router.post("/tasks/{task_id}/duplicate", response_model=TaskDetailResponse, status_code=status.HTTP_201_CREATED)
def duplicate_task(task_id: str, payload: TaskDuplicateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.duplicate_task(db, current_user, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    service.delete_task(db, current_user, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/members", response_model=list[MemberSummaryResponse])
def list_members(db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.list_members(db, current_user)


@router.post("/members", response_model=MemberDetailResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.create_member(db, current_user, payload)


@router.get("/members/{member_id}", response_model=MemberDetailResponse)
def get_member(member_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.get_member(db, current_user, member_id)


@router.put("/members/{member_id}", response_model=MemberDetailResponse)
def update_member(member_id: str, payload: MemberUpdateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.update_member(db, current_user, member_id, payload)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    service.delete_member(db, current_user, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=list[CategorySummaryResponse])
def list_categories(db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=CategoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.create_category(db, current_user, payload)


@router.get("/categories/{category_id}", response_model=CategoryDetailResponse)
def get_category(category_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.get_category(db, current_user, category_id)


@router.put("/categories/{category_id}", response_model=CategoryDetailResponse)
def update_category(category_id: str, payload: CategoryUpdateRequest, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: FamilyTaskPlannerDB, current_user: CurrentFamilyTaskPlannerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
