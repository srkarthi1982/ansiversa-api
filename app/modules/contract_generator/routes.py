from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.contract_generator.db import get_contract_generator_db
from app.modules.contract_generator.schemas import (
    ContractDashboardResponse,
    ContractDocumentCreateRequest,
    ContractDocumentDetailResponse,
    ContractDocumentUpdateRequest,
    ContractHistoryCreateRequest,
    ContractHistorySummaryResponse,
    ContractClauseCreateRequest,
    ContractClauseDetailResponse,
    ContractClauseUpdateRequest,
    ContractProjectCreateRequest,
    ContractProjectDetailResponse,
    ContractProjectUpdateRequest,
)
from app.modules.contract_generator.service import (
    create_document,
    create_history_item,
    create_clause,
    create_project,
    delete_document,
    delete_history_item,
    delete_clause,
    delete_project,
    get_dashboard,
    get_document,
    get_clause,
    get_project,
    update_document,
    update_clause,
    update_project,
)

router = APIRouter()


@router.get("/dashboard", response_model=ContractDashboardResponse)
def get_contract_dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractDashboardResponse:
    return get_dashboard(db, current_user)


@router.post(
    "/projects",
    response_model=ContractProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_project(
    payload: ContractProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractProjectDetailResponse:
    return create_project(db, current_user, payload)


@router.get("/projects/{project_id}", response_model=ContractProjectDetailResponse)
def get_contract_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractProjectDetailResponse:
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=ContractProjectDetailResponse)
def update_contract_project(
    project_id: Annotated[int, Path(gt=0)],
    payload: ContractProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractProjectDetailResponse:
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_project(
    project_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> None:
    delete_project(db, current_user, project_id)


@router.post(
    "/documents",
    response_model=ContractDocumentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_document(
    payload: ContractDocumentCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractDocumentDetailResponse:
    return create_document(db, current_user, payload)


@router.get("/documents/{document_id}", response_model=ContractDocumentDetailResponse)
def get_contract_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractDocumentDetailResponse:
    return get_document(db, current_user, document_id)


@router.put("/documents/{document_id}", response_model=ContractDocumentDetailResponse)
def update_contract_document(
    document_id: Annotated[int, Path(gt=0)],
    payload: ContractDocumentUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractDocumentDetailResponse:
    return update_document(db, current_user, document_id, payload)


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_document(
    document_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> None:
    delete_document(db, current_user, document_id)


@router.post(
    "/clauses",
    response_model=ContractClauseDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_item(
    payload: ContractClauseCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractClauseDetailResponse:
    return create_clause(db, current_user, payload)


@router.get("/clauses/{clause_id}", response_model=ContractClauseDetailResponse)
def get_contract_item(
    clause_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractClauseDetailResponse:
    return get_clause(db, current_user, clause_id)


@router.put("/clauses/{clause_id}", response_model=ContractClauseDetailResponse)
def update_contract_item(
    clause_id: Annotated[int, Path(gt=0)],
    payload: ContractClauseUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractClauseDetailResponse:
    return update_clause(db, current_user, clause_id, payload)


@router.delete("/clauses/{clause_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_item(
    clause_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> None:
    delete_clause(db, current_user, clause_id)


@router.post(
    "/history",
    response_model=ContractHistorySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_history_item(
    payload: ContractHistoryCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> ContractHistorySummaryResponse:
    return create_history_item(db, current_user, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract_history_item(
    history_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_contract_generator_db)],
) -> None:
    delete_history_item(db, current_user, history_id)
