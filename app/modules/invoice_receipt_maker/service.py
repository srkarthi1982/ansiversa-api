from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.invoice_receipt_maker.models import (
    InvoiceReceiptDocument,
    InvoiceReceiptHistoryItem,
    InvoiceReceiptItem,
    InvoiceReceiptProject,
)
from app.modules.invoice_receipt_maker.schemas import (
    InvoiceReceiptDashboardResponse,
    InvoiceReceiptDocumentCreateRequest,
    InvoiceReceiptDocumentDetailResponse,
    InvoiceReceiptDocumentSummaryResponse,
    InvoiceReceiptDocumentUpdateRequest,
    InvoiceReceiptHistoryCreateRequest,
    InvoiceReceiptHistorySummaryResponse,
    InvoiceReceiptItemCreateRequest,
    InvoiceReceiptItemDetailResponse,
    InvoiceReceiptItemSummaryResponse,
    InvoiceReceiptItemUpdateRequest,
    InvoiceReceiptProjectCreateRequest,
    InvoiceReceiptProjectDetailResponse,
    InvoiceReceiptProjectSummaryResponse,
    InvoiceReceiptProjectUpdateRequest,
)

PREVIEW_LENGTH = 220
MONEY_QUANT = Decimal("0.01")


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _line_total(quantity: Decimal, unit_price: Decimal, tax_rate: Decimal) -> Decimal:
    subtotal = _money(quantity * unit_price)
    tax = _money(subtotal * (tax_rate / Decimal("100")))
    return _money(subtotal + tax)


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> InvoiceReceiptProject:
    project = db.get(InvoiceReceiptProject, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Invoice and receipt project was not found.")

    return project


def _get_owned_document(db: Session, user: User, document_id: int) -> InvoiceReceiptDocument:
    document = db.get(InvoiceReceiptDocument, document_id)
    if not document or document.owner_id != user.id:
        _not_found("Invoice or receipt document was not found.")

    return document


def _get_owned_item(db: Session, user: User, item_id: int) -> InvoiceReceiptItem:
    item = db.get(InvoiceReceiptItem, item_id)
    if not item or item.owner_id != user.id:
        _not_found("Invoice or receipt line item was not found.")

    return item


def _get_owned_history_item(
    db: Session,
    user: User,
    history_id: int,
) -> InvoiceReceiptHistoryItem:
    history_item = db.get(InvoiceReceiptHistoryItem, history_id)
    if not history_item or history_item.owner_id != user.id:
        _not_found("Invoice and receipt history item was not found.")

    return history_item


def _optional_owned_project(
    db: Session,
    user: User,
    project_id: int | None,
) -> InvoiceReceiptProject | None:
    if project_id is None:
        return None

    return _get_owned_project(db, user, project_id)


def _optional_owned_document(
    db: Session,
    user: User,
    document_id: int | None,
) -> InvoiceReceiptDocument | None:
    if document_id is None:
        return None

    return _get_owned_document(db, user, document_id)


def _count_documents(db: Session, project_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(InvoiceReceiptDocument).where(
                InvoiceReceiptDocument.project_id == project_id
            )
        ).scalar_one()
    )


def _count_items(db: Session, document_id: int) -> int:
    return int(
        db.execute(
            select(func.count()).select_from(InvoiceReceiptItem).where(
                InvoiceReceiptItem.document_id == document_id
            )
        ).scalar_one()
    )


def _recalculate_document_totals(db: Session, document: InvoiceReceiptDocument) -> None:
    items = list(
        db.execute(
            select(InvoiceReceiptItem).where(
                InvoiceReceiptItem.document_id == document.id
            )
        )
        .scalars()
        .all()
    )
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for item in items:
        item_subtotal = _money(Decimal(item.quantity) * Decimal(item.unit_price))
        item_tax = _money(item_subtotal * (Decimal(item.tax_rate) / Decimal("100")))
        subtotal += item_subtotal
        tax_total += item_tax

    document.subtotal = _money(subtotal)
    document.tax_total = _money(tax_total)
    document.total = _money(subtotal + tax_total)


def _project_summary_response(
    db: Session,
    project: InvoiceReceiptProject,
) -> InvoiceReceiptProjectSummaryResponse:
    return InvoiceReceiptProjectSummaryResponse(
        id=project.id,
        title=project.title,
        business_name=project.business_name,
        client_name=project.client_name,
        currency=project.currency,
        status=project.status,
        document_count=_count_documents(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(
    db: Session,
    project: InvoiceReceiptProject,
) -> InvoiceReceiptProjectDetailResponse:
    summary = _project_summary_response(db, project)
    return InvoiceReceiptProjectDetailResponse(
        **summary.model_dump(),
        notes=project.notes,
    )


def _document_summary_response(
    db: Session,
    document: InvoiceReceiptDocument,
    project_title: str,
) -> InvoiceReceiptDocumentSummaryResponse:
    return InvoiceReceiptDocumentSummaryResponse(
        id=document.id,
        project_id=document.project_id,
        project_title=project_title,
        document_type=document.document_type,
        document_number=document.document_number,
        title=document.title,
        client_name=document.client_name,
        issue_date=document.issue_date,
        due_date=document.due_date,
        paid_date=document.paid_date,
        status=document.status,
        subtotal=Decimal(document.subtotal),
        tax_total=Decimal(document.tax_total),
        total=Decimal(document.total),
        item_count=_count_items(db, document.id),
        notes_preview=_preview(document.notes),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _document_detail_response(
    db: Session,
    document: InvoiceReceiptDocument,
    project_title: str,
) -> InvoiceReceiptDocumentDetailResponse:
    summary = _document_summary_response(db, document, project_title)
    return InvoiceReceiptDocumentDetailResponse(
        **summary.model_dump(),
        notes=document.notes,
        terms=document.terms,
    )


def _item_summary_response(
    item: InvoiceReceiptItem,
    document_title: str,
) -> InvoiceReceiptItemSummaryResponse:
    return InvoiceReceiptItemSummaryResponse(
        id=item.id,
        document_id=item.document_id,
        document_title=document_title,
        description_preview=_preview(item.description) or "",
        quantity=Decimal(item.quantity),
        unit_price=Decimal(item.unit_price),
        tax_rate=Decimal(item.tax_rate),
        line_total=Decimal(item.line_total),
        sort_order=item.sort_order,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _item_detail_response(
    item: InvoiceReceiptItem,
    document_title: str,
) -> InvoiceReceiptItemDetailResponse:
    return InvoiceReceiptItemDetailResponse(
        id=item.id,
        document_id=item.document_id,
        document_title=document_title,
        description=item.description,
        quantity=Decimal(item.quantity),
        unit_price=Decimal(item.unit_price),
        tax_rate=Decimal(item.tax_rate),
        line_total=Decimal(item.line_total),
        sort_order=item.sort_order,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _history_summary_response(
    history_item: InvoiceReceiptHistoryItem,
    project_title: str | None,
    document_title: str | None,
) -> InvoiceReceiptHistorySummaryResponse:
    return InvoiceReceiptHistorySummaryResponse(
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


def list_projects(db: Session, user: User) -> list[InvoiceReceiptProjectSummaryResponse]:
    projects = list(
        db.execute(
            select(InvoiceReceiptProject)
            .where(InvoiceReceiptProject.owner_id == user.id)
            .order_by(InvoiceReceiptProject.updated_at.desc(), InvoiceReceiptProject.title.asc())
        )
        .scalars()
        .all()
    )

    return [_project_summary_response(db, project) for project in projects]


def create_project(
    db: Session,
    user: User,
    payload: InvoiceReceiptProjectCreateRequest,
) -> InvoiceReceiptProjectDetailResponse:
    project = InvoiceReceiptProject(
        owner_id=user.id,
        title=payload.title,
        business_name=payload.business_name,
        client_name=payload.client_name,
        currency=payload.currency.upper(),
        status=payload.status,
        notes=payload.notes,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return _project_detail_response(db, project)


def get_project(
    db: Session,
    user: User,
    project_id: int,
) -> InvoiceReceiptProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    return _project_detail_response(db, project)


def update_project(
    db: Session,
    user: User,
    project_id: int,
    payload: InvoiceReceiptProjectUpdateRequest,
) -> InvoiceReceiptProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "currency" and isinstance(value, str):
            value = value.upper()
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    document_ids = [
        row[0]
        for row in db.execute(
            select(InvoiceReceiptDocument.id).where(
                InvoiceReceiptDocument.project_id == project.id
            )
        ).all()
    ]
    if document_ids:
        db.execute(delete(InvoiceReceiptItem).where(InvoiceReceiptItem.document_id.in_(document_ids)))
        db.execute(delete(InvoiceReceiptHistoryItem).where(InvoiceReceiptHistoryItem.document_id.in_(document_ids)))
    db.execute(delete(InvoiceReceiptHistoryItem).where(InvoiceReceiptHistoryItem.project_id == project.id))
    db.execute(delete(InvoiceReceiptDocument).where(InvoiceReceiptDocument.project_id == project.id))
    db.delete(project)
    db.commit()


def list_documents(db: Session, user: User) -> list[InvoiceReceiptDocumentSummaryResponse]:
    rows = db.execute(
        select(InvoiceReceiptDocument, InvoiceReceiptProject.title)
        .join(InvoiceReceiptProject, InvoiceReceiptProject.id == InvoiceReceiptDocument.project_id)
        .where(InvoiceReceiptDocument.owner_id == user.id)
        .order_by(InvoiceReceiptDocument.updated_at.desc(), InvoiceReceiptDocument.title.asc())
    ).all()

    return [_document_summary_response(db, document, project_title) for document, project_title in rows]


def create_document(
    db: Session,
    user: User,
    payload: InvoiceReceiptDocumentCreateRequest,
) -> InvoiceReceiptDocumentDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    document = InvoiceReceiptDocument(
        project_id=project.id,
        owner_id=user.id,
        document_type=payload.document_type,
        document_number=payload.document_number,
        title=payload.title,
        client_name=payload.client_name,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        paid_date=payload.paid_date,
        status=payload.status,
        notes=payload.notes,
        terms=payload.terms,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return _document_detail_response(db, document, project.title)


def get_document(
    db: Session,
    user: User,
    document_id: int,
) -> InvoiceReceiptDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    project = _get_owned_project(db, user, document.project_id)
    return _document_detail_response(db, document, project.title)


def update_document(
    db: Session,
    user: User,
    document_id: int,
    payload: InvoiceReceiptDocumentUpdateRequest,
) -> InvoiceReceiptDocumentDetailResponse:
    document = _get_owned_document(db, user, document_id)
    project = _get_owned_project(db, user, document.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    db.commit()
    db.refresh(document)

    return _document_detail_response(db, document, project.title)


def delete_document(db: Session, user: User, document_id: int) -> None:
    document = _get_owned_document(db, user, document_id)
    db.execute(delete(InvoiceReceiptHistoryItem).where(InvoiceReceiptHistoryItem.document_id == document.id))
    db.execute(delete(InvoiceReceiptItem).where(InvoiceReceiptItem.document_id == document.id))
    db.delete(document)
    db.commit()


def list_items(db: Session, user: User) -> list[InvoiceReceiptItemSummaryResponse]:
    rows = db.execute(
        select(InvoiceReceiptItem, InvoiceReceiptDocument.title)
        .join(InvoiceReceiptDocument, InvoiceReceiptDocument.id == InvoiceReceiptItem.document_id)
        .where(InvoiceReceiptItem.owner_id == user.id)
        .order_by(
            InvoiceReceiptItem.document_id.asc(),
            InvoiceReceiptItem.sort_order.asc(),
            InvoiceReceiptItem.updated_at.desc(),
        )
    ).all()

    return [_item_summary_response(item, document_title) for item, document_title in rows]


def create_item(
    db: Session,
    user: User,
    payload: InvoiceReceiptItemCreateRequest,
) -> InvoiceReceiptItemDetailResponse:
    document = _get_owned_document(db, user, payload.document_id)
    item = InvoiceReceiptItem(
        document_id=document.id,
        owner_id=user.id,
        description=payload.description,
        quantity=_money(payload.quantity),
        unit_price=_money(payload.unit_price),
        tax_rate=_money(payload.tax_rate),
        line_total=_line_total(payload.quantity, payload.unit_price, payload.tax_rate),
        sort_order=payload.sort_order,
    )
    db.add(item)
    db.flush()
    _recalculate_document_totals(db, document)
    db.commit()
    db.refresh(item)

    return _item_detail_response(item, document.title)


def get_item(db: Session, user: User, item_id: int) -> InvoiceReceiptItemDetailResponse:
    item = _get_owned_item(db, user, item_id)
    document = _get_owned_document(db, user, item.document_id)
    return _item_detail_response(item, document.title)


def update_item(
    db: Session,
    user: User,
    item_id: int,
    payload: InvoiceReceiptItemUpdateRequest,
) -> InvoiceReceiptItemDetailResponse:
    item = _get_owned_item(db, user, item_id)
    document = _get_owned_document(db, user, item.document_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"quantity", "unit_price", "tax_rate"}:
            value = _money(value)
        setattr(item, field, value)
    item.line_total = _line_total(
        Decimal(item.quantity),
        Decimal(item.unit_price),
        Decimal(item.tax_rate),
    )
    _recalculate_document_totals(db, document)
    db.commit()
    db.refresh(item)

    return _item_detail_response(item, document.title)


def delete_item(db: Session, user: User, item_id: int) -> None:
    item = _get_owned_item(db, user, item_id)
    document = _get_owned_document(db, user, item.document_id)
    db.delete(item)
    db.flush()
    _recalculate_document_totals(db, document)
    db.commit()


def list_history(db: Session, user: User) -> list[InvoiceReceiptHistorySummaryResponse]:
    rows = db.execute(
        select(InvoiceReceiptHistoryItem, InvoiceReceiptProject.title, InvoiceReceiptDocument.title)
        .outerjoin(InvoiceReceiptProject, InvoiceReceiptProject.id == InvoiceReceiptHistoryItem.project_id)
        .outerjoin(InvoiceReceiptDocument, InvoiceReceiptDocument.id == InvoiceReceiptHistoryItem.document_id)
        .where(InvoiceReceiptHistoryItem.owner_id == user.id)
        .order_by(InvoiceReceiptHistoryItem.created_at.desc())
    ).all()

    return [
        _history_summary_response(history_item, project_title, document_title)
        for history_item, project_title, document_title in rows
    ]


def create_history_item(
    db: Session,
    user: User,
    payload: InvoiceReceiptHistoryCreateRequest,
) -> InvoiceReceiptHistorySummaryResponse:
    project = _optional_owned_project(db, user, payload.project_id)
    document = _optional_owned_document(db, user, payload.document_id)
    if project and document and document.project_id != project.id:
        _bad_request("Invoice and receipt history document must belong to the selected project.")
    if document and project is None:
        project = _get_owned_project(db, user, document.project_id)

    history_item = InvoiceReceiptHistoryItem(
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


def get_dashboard(db: Session, user: User) -> InvoiceReceiptDashboardResponse:
    projects = list_projects(db, user)
    documents = list_documents(db, user)
    items = list_items(db, user)
    history = list_history(db, user)

    return InvoiceReceiptDashboardResponse(
        projects=projects,
        documents=documents,
        items=items,
        history=history,
        active_project_count=sum(1 for project in projects if project.status == "active"),
        draft_document_count=sum(1 for document in documents if document.status == "draft"),
        sent_document_count=sum(1 for document in documents if document.status == "sent"),
        paid_document_count=sum(1 for document in documents if document.status == "paid"),
    )
