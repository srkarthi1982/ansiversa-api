from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.contract_generator.models import (
    ContractClause,
    ContractDocument,
    ContractHistoryItem,
    ContractProject,
)
from app.modules.contract_generator.schemas import (
    ContractClauseCreateRequest,
    ContractClauseDetailResponse,
    ContractClauseSummaryResponse,
    ContractClauseUpdateRequest,
    ContractDashboardResponse,
    ContractDocumentCreateRequest,
    ContractDocumentDetailResponse,
    ContractDocumentSummaryResponse,
    ContractDocumentUpdateRequest,
    ContractHistoryCreateRequest,
    ContractHistorySummaryResponse,
    ContractProjectCreateRequest,
    ContractProjectDetailResponse,
    ContractProjectSummaryResponse,
    ContractProjectUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> ContractProject:
    project = db.get(ContractProject, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Contract project was not found.")
    return project


def _get_owned_document(db: Session, user: User, document_id: int) -> ContractDocument:
    document = db.get(ContractDocument, document_id)
    if not document or document.owner_id != user.id:
        _not_found("Contract document was not found.")
    return document


def _get_owned_clause(db: Session, user: User, clause_id: int) -> ContractClause:
    clause = db.get(ContractClause, clause_id)
    if not clause or clause.owner_id != user.id:
        _not_found("Contract clause was not found.")
    return clause


def _get_owned_history_item(db: Session, user: User, history_id: int) -> ContractHistoryItem:
    history_item = db.get(ContractHistoryItem, history_id)
    if not history_item or history_item.owner_id != user.id:
        _not_found("Contract history item was not found.")
    return history_item


def _optional_owned_project(db: Session, user: User, project_id: int | None) -> ContractProject | None:
    if project_id is None:
        return None
    return _get_owned_project(db, user, project_id)


def _optional_owned_document(db: Session, user: User, document_id: int | None) -> ContractDocument | None:
    if document_id is None:
        return None
    return _get_owned_document(db, user, document_id)


def _count_documents(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ContractDocument).where(
                ContractDocument.project_id == project_id
            )
        ).scalar_one()
    )


def _count_clauses(db: Session, document_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(ContractClause).where(
                ContractClause.document_id == document_id
            )
        ).scalar_one()
    )


def _project_summary_response(db: Session, project: ContractProject) -> ContractProjectSummaryResponse:
    return ContractProjectSummaryResponse(
        id=project.id,
        title=project.title,
        counterparty_name=project.counterparty_name,
        contract_type=project.contract_type,
        status=project.status,
        document_count=_count_documents(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: ContractProject) -> ContractProjectDetailResponse:
    summary = _project_summary_response(db, project)
    return ContractProjectDetailResponse(**summary.model_dump(), notes=project.notes)


def _document_summary_response(
    db: Session,
    document: ContractDocument,
    project_title: str,
) -> ContractDocumentSummaryResponse:
    return ContractDocumentSummaryResponse(
        id=document.id,
        project_id=document.project_id,
        project_title=project_title,
        title=document.title,
        status=document.status,
        contract_type=document.contract_type,
        effective_date=document.effective_date,
        expiry_date=document.expiry_date,
        jurisdiction=document.jurisdiction,
        clause_count=_count_clauses(db, document.id),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _document_detail_response(
    db: Session,
    document: ContractDocument,
    project_title: str,
) -> ContractDocumentDetailResponse:
    summary = _document_summary_response(db, document, project_title)
    return ContractDocumentDetailResponse(
        **summary.model_dump(),
        parties=document.parties,
        body=document.body,
        notes=document.notes,
    )


def _clause_summary_response(
    clause: ContractClause,
    document_title: str,
) -> ContractClauseSummaryResponse:
    return ContractClauseSummaryResponse(
        id=clause.id,
        document_id=clause.document_id,
        document_title=document_title,
        title=clause.title,
        category=clause.category,
        sort_order=clause.sort_order,
        created_at=clause.created_at,
        updated_at=clause.updated_at,
    )


def _clause_detail_response(
    clause: ContractClause,
    document_title: str,
) -> ContractClauseDetailResponse:
    summary = _clause_summary_response(clause, document_title)
    return ContractClauseDetailResponse(**summary.model_dump(), body=clause.body)


def _history_summary_response(
    history_item: ContractHistoryItem,
    project_title: str | None,
    document_title: str | None,
) -> ContractHistorySummaryResponse:
    return ContractHistorySummaryResponse(
        id=history_item.id,
        project_id=history_item.project_id,
        project_title=project_title,
        document_id=history_item.document_id,
        document_title=document_title,
        title=history_item.title,
        action_type=history_item.action_type,
        notes_preview=_preview(history_item.notes),
        created_at=history_item.created_at,
        updated_at=history_item.updated_at,
    )


def list_projects(db: Session, user: User) -> list[ContractProjectSummaryResponse]:
    projects = list(
        db.execute(
            select(ContractProject)
            .where(ContractProject.owner_id == user.id)
            .order_by(ContractProject.updated_at.desc(), ContractProject.title.asc())
        )
        .scalars()
        .all()
    )
    return [_project_summary_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: ContractProjectCreateRequest,
) -> ContractProjectDetailResponse:
    project = ContractProject(
        owner_id=user.id,
        title=payload.title,
        counterparty_name=payload.counterparty_name,
        contract_type=payload.contract_type,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> ContractProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: ContractProjectUpdateRequest,
) -> ContractProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    document_ids = [
        row[0]
        for row in db.execute(
            select(ContractDocument.id).where(ContractDocument.project_id == project.id)
        ).all()
    ]
    if document_ids:
        db.execute(delete(ContractClause).where(ContractClause.document_id.in_(document_ids)))
        db.execute(delete(ContractHistoryItem).where(ContractHistoryItem.document_id.in_(document_ids)))
    db.execute(delete(ContractHistoryItem).where(ContractHistoryItem.project_id == project.id))
    db.execute(delete(ContractDocument).where(ContractDocument.project_id == project.id))
    db.delete(project)
    db.commit()


def list_documents(db: Session, user: User) -> list[ContractDocumentSummaryResponse]:
    rows = db.execute(
        select(ContractDocument, ContractProject.title)
        .join(ContractProject, ContractProject.id == ContractDocument.project_id)
        .where(ContractDocument.owner_id == user.id)
        .order_by(ContractDocument.updated_at.desc(), ContractDocument.title.asc())
    ).all()
    return [_document_summary_response(db, document, project_title) for document, project_title in rows]


def create_document(
    db: Session,
    user: User,
    payload: ContractDocumentCreateRequest,
) -> ContractDocumentDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    document = ContractDocument(
        project_id=project.id,
        owner_id=user.id,
        title=payload.title,
        status=payload.status,
        contract_type=payload.contract_type,
        effective_date=payload.effective_date,
        expiry_date=payload.expiry_date,
        jurisdiction=payload.jurisdiction,
        parties=payload.parties,
        body=payload.body,
        notes=payload.notes,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return _document_detail_response(db, document, project.title)


def get_document(db: Session, user: User, document_id: int) -> ContractDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    project = _get_owned_project(db, user, document.project_id)
    return _document_detail_response(db, document, project.title)


def update_document(
    db: Session,
    user: User,
    document_id: int,
    payload: ContractDocumentUpdateRequest,
) -> ContractDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    project = _get_owned_project(db, user, document.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)
    return _document_detail_response(db, document, project.title)


def delete_document(db: Session, user: User, document_id: int) -> None:
    document = _get_owned_document(db, user, document_id)
    db.execute(delete(ContractHistoryItem).where(ContractHistoryItem.document_id == document.id))
    db.execute(delete(ContractClause).where(ContractClause.document_id == document.id))
    db.delete(document)
    db.commit()


def list_clauses(db: Session, user: User) -> list[ContractClauseSummaryResponse]:
    rows = db.execute(
        select(ContractClause, ContractDocument.title)
        .join(ContractDocument, ContractDocument.id == ContractClause.document_id)
        .where(ContractClause.owner_id == user.id)
        .order_by(
            ContractClause.document_id.asc(),
            ContractClause.sort_order.asc(),
            ContractClause.updated_at.desc(),
        )
    ).all()
    return [_clause_summary_response(clause, document_title) for clause, document_title in rows]


def create_clause(
    db: Session,
    user: User,
    payload: ContractClauseCreateRequest,
) -> ContractClauseDetailResponse:
    document = _get_owned_document(db, user, payload.document_id)
    clause = ContractClause(
        document_id=document.id,
        owner_id=user.id,
        title=payload.title,
        category=payload.category,
        body=payload.body,
        sort_order=payload.sort_order,
    )
    db.add(clause)
    db.commit()
    db.refresh(clause)
    return _clause_detail_response(clause, document.title)


def get_clause(db: Session, user: User, clause_id: int) -> ContractClauseDetailResponse:
    clause = _get_owned_clause(db, user, clause_id)
    document = _get_owned_document(db, user, clause.document_id)
    return _clause_detail_response(clause, document.title)


def update_clause(
    db: Session,
    user: User,
    clause_id: int,
    payload: ContractClauseUpdateRequest,
) -> ContractClauseDetailResponse:
    clause = _get_owned_clause(db, user, clause_id)
    document = _get_owned_document(db, user, clause.document_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(clause, field, value)
    db.commit()
    db.refresh(clause)
    return _clause_detail_response(clause, document.title)


def delete_clause(db: Session, user: User, clause_id: int) -> None:
    clause = _get_owned_clause(db, user, clause_id)
    db.delete(clause)
    db.commit()


def list_history(db: Session, user: User) -> list[ContractHistorySummaryResponse]:
    rows = db.execute(
        select(ContractHistoryItem, ContractProject.title, ContractDocument.title)
        .outerjoin(ContractProject, ContractProject.id == ContractHistoryItem.project_id)
        .outerjoin(ContractDocument, ContractDocument.id == ContractHistoryItem.document_id)
        .where(ContractHistoryItem.owner_id == user.id)
        .order_by(ContractHistoryItem.created_at.desc())
    ).all()
    return [
        _history_summary_response(history_item, project_title, document_title)
        for history_item, project_title, document_title in rows
    ]


def create_history_item(
    db: Session,
    user: User,
    payload: ContractHistoryCreateRequest,
) -> ContractHistorySummaryResponse:
    project = _optional_owned_project(db, user, payload.project_id)
    document = _optional_owned_document(db, user, payload.document_id)
    if project and document and document.project_id != project.id:
        _bad_request("Contract history document must belong to the selected project.")
    if document and project is None:
        project = _get_owned_project(db, user, document.project_id)

    history_item = ContractHistoryItem(
        project_id=project.id if project else None,
        document_id=document.id if document else None,
        owner_id=user.id,
        title=payload.title,
        action_type=payload.action_type,
        notes=payload.notes,
    )
    db.add(history_item)
    db.commit()
    db.refresh(history_item)
    return _history_summary_response(
        history_item,
        project.title if project else None,
        document.title if document else None,
    )


def delete_history_item(db: Session, user: User, history_id: int) -> None:
    history_item = _get_owned_history_item(db, user, history_id)
    db.delete(history_item)
    db.commit()


def get_dashboard(db: Session, user: User) -> ContractDashboardResponse:
    projects = list_projects(db, user)
    documents = list_documents(db, user)
    clauses = list_clauses(db, user)
    history = list_history(db, user)
    return ContractDashboardResponse(
        projects=projects,
        documents=documents,
        clauses=clauses,
        history=history,
        active_project_count=sum(1 for project in projects if project.status == "active"),
        draft_document_count=sum(1 for document in documents if document.status == "draft"),
        review_document_count=sum(1 for document in documents if document.status == "review"),
        signed_document_count=sum(1 for document in documents if document.status == "signed"),
    )
