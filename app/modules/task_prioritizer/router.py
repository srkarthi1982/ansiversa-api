from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.task_prioritizer.dependencies import CurrentUser, TaskPrioritizerDb
from app.modules.task_prioritizer.schemas import (
    TaskPrioritizerDashboardResponse,
    TaskPrioritizerHistoryResponse,
    TaskPrioritizerPriorityAssignRequest,
    TaskPrioritizerRuleCreateRequest,
    TaskPrioritizerRuleResponse,
    TaskPrioritizerRuleUpdateRequest,
    TaskPrioritizerTaskCreateRequest,
    TaskPrioritizerTaskDetailResponse,
    TaskPrioritizerTaskSummaryResponse,
    TaskPrioritizerTaskUpdateRequest,
)
from app.modules.task_prioritizer.service import (
    assign_priority,
    create_rule,
    create_task,
    delete_rule,
    delete_task,
    duplicate_task,
    get_dashboard,
    get_task,
    list_history,
    list_rules,
    list_tasks,
    recalculate_priorities,
    update_rule,
    update_task,
)

router = APIRouter()


@router.get("/dashboard", response_model=TaskPrioritizerDashboardResponse)
def get_task_prioritizer_dashboard(current_user: CurrentUser, db: TaskPrioritizerDb) -> TaskPrioritizerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/tasks", response_model=TaskPrioritizerTaskDetailResponse, status_code=status.HTTP_201_CREATED)
def create_task_prioritizer_task(
    payload: TaskPrioritizerTaskCreateRequest,
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerTaskDetailResponse:
    return create_task(db, current_user, payload)


@router.get("/tasks", response_model=list[TaskPrioritizerTaskSummaryResponse])
def list_task_prioritizer_tasks(current_user: CurrentUser, db: TaskPrioritizerDb) -> list[TaskPrioritizerTaskSummaryResponse]:
    return list_tasks(db, current_user)


@router.post("/tasks/recalculate", response_model=TaskPrioritizerDashboardResponse)
def recalculate_task_prioritizer_tasks(current_user: CurrentUser, db: TaskPrioritizerDb) -> TaskPrioritizerDashboardResponse:
    return recalculate_priorities(db, current_user)


@router.get("/tasks/{task_id}", response_model=TaskPrioritizerTaskDetailResponse)
def get_task_prioritizer_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerTaskDetailResponse:
    return get_task(db, current_user, task_id)


@router.put("/tasks/{task_id}", response_model=TaskPrioritizerTaskDetailResponse)
def update_task_prioritizer_task(
    task_id: Annotated[int, Path(gt=0)],
    payload: TaskPrioritizerTaskUpdateRequest,
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerTaskDetailResponse:
    return update_task(db, current_user, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_prioritizer_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> None:
    delete_task(db, current_user, task_id)


@router.post("/tasks/{task_id}/duplicate", response_model=TaskPrioritizerTaskDetailResponse, status_code=status.HTTP_201_CREATED)
def duplicate_task_prioritizer_task(
    task_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerTaskDetailResponse:
    return duplicate_task(db, current_user, task_id)


@router.post("/tasks/{task_id}/priority", response_model=TaskPrioritizerTaskDetailResponse)
def assign_task_prioritizer_priority(
    task_id: Annotated[int, Path(gt=0)],
    payload: TaskPrioritizerPriorityAssignRequest,
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerTaskDetailResponse:
    return assign_priority(db, current_user, task_id, payload)


@router.post("/rules", response_model=TaskPrioritizerRuleResponse, status_code=status.HTTP_201_CREATED)
def create_task_prioritizer_rule(
    payload: TaskPrioritizerRuleCreateRequest,
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerRuleResponse:
    return create_rule(db, current_user, payload)


@router.get("/rules", response_model=list[TaskPrioritizerRuleResponse])
def list_task_prioritizer_rules(current_user: CurrentUser, db: TaskPrioritizerDb) -> list[TaskPrioritizerRuleResponse]:
    return list_rules(db, current_user)


@router.put("/rules/{rule_id}", response_model=TaskPrioritizerRuleResponse)
def update_task_prioritizer_rule(
    rule_id: Annotated[int, Path(gt=0)],
    payload: TaskPrioritizerRuleUpdateRequest,
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> TaskPrioritizerRuleResponse:
    return update_rule(db, current_user, rule_id, payload)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_prioritizer_rule(
    rule_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: TaskPrioritizerDb,
) -> None:
    delete_rule(db, current_user, rule_id)


@router.get("/history", response_model=list[TaskPrioritizerHistoryResponse])
def list_task_prioritizer_history(current_user: CurrentUser, db: TaskPrioritizerDb) -> list[TaskPrioritizerHistoryResponse]:
    return list_history(db, current_user)
