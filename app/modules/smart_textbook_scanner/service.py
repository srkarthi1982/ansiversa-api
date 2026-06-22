from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.smart_textbook_scanner.models import (
    ExtractedNote,
    TextbookPage,
    TextbookScan,
)
from app.modules.smart_textbook_scanner.schemas import (
    ExtractedNoteCreateRequest,
    ExtractedNoteResponse,
    SmartTextbookScannerDashboardResponse,
    SmartTextbookScannerReviewResponse,
    TextbookPageCreateRequest,
    TextbookPageResponse,
    TextbookPageUpdateRequest,
    TextbookScanCreateRequest,
    TextbookScanResponse,
    TextbookScanUpdateRequest,
)


def _count_pages(db: Session, scan_id: int, *, status_value: str | None = None) -> int:
    statement = select(func.count()).select_from(TextbookPage).where(
        TextbookPage.scan_id == scan_id
    )
    if status_value is not None:
        statement = statement.where(TextbookPage.status == status_value)

    return int(db.execute(statement).scalar_one())


def _count_notes(
    db: Session,
    *,
    owner_id: str | None = None,
    scan_id: int | None = None,
    page_id: int | None = None,
) -> int:
    statement = select(func.count()).select_from(ExtractedNote)
    if owner_id is not None:
        statement = statement.where(ExtractedNote.owner_id == owner_id)
    if scan_id is not None:
        statement = statement.where(ExtractedNote.scan_id == scan_id)
    if page_id is not None:
        statement = statement.where(ExtractedNote.page_id == page_id)

    return int(db.execute(statement).scalar_one())


def _rate(total_count: int, completed_count: int) -> int:
    return round((completed_count / total_count) * 100) if total_count else 0


def _scan_response(db: Session, scan: TextbookScan) -> TextbookScanResponse:
    return TextbookScanResponse(
        id=scan.id,
        title=scan.title,
        subject=scan.subject,
        source=scan.source,
        goal=scan.goal,
        status=scan.status,
        page_count=_count_pages(db, scan.id),
        extracted_note_count=_count_notes(db, scan_id=scan.id),
        created_at=scan.created_at,
        updated_at=scan.updated_at,
    )


def _page_response(db: Session, page: TextbookPage, scan_title: str) -> TextbookPageResponse:
    return TextbookPageResponse(
        id=page.id,
        scan_id=page.scan_id,
        scan_title=scan_title,
        page_number=page.page_number,
        title=page.title,
        page_text=page.page_text,
        status=page.status,
        extracted_note_count=_count_notes(db, page_id=page.id),
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


def _note_response(
    note: ExtractedNote,
    scan_title: str,
    page_number: int,
) -> ExtractedNoteResponse:
    return ExtractedNoteResponse(
        id=note.id,
        scan_id=note.scan_id,
        scan_title=scan_title,
        page_id=note.page_id,
        page_number=page_number,
        heading=note.heading,
        key_points=note.key_points,
        summary=note.summary,
        note_type=note.note_type,
        created_at=note.created_at,
    )


def _get_owned_scan(db: Session, user: User, scan_id: int) -> TextbookScan:
    scan = db.get(TextbookScan, scan_id)
    if not scan or scan.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Textbook scan was not found.",
        )

    return scan


def _get_owned_page(db: Session, user: User, page_id: int) -> TextbookPage:
    page = db.get(TextbookPage, page_id)
    if not page or page.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Textbook page was not found.",
        )

    return page


def list_scans(db: Session, user: User) -> list[TextbookScanResponse]:
    scans = list(
        db.execute(
            select(TextbookScan)
            .where(TextbookScan.owner_id == user.id)
            .order_by(TextbookScan.updated_at.desc(), TextbookScan.title.asc())
        )
        .scalars()
        .all()
    )

    return [_scan_response(db, scan) for scan in scans]


def create_scan(
    db: Session,
    user: User,
    payload: TextbookScanCreateRequest,
) -> TextbookScanResponse:
    scan = TextbookScan(
        owner_id=user.id,
        title=payload.title,
        subject=payload.subject,
        source=payload.source,
        goal=payload.goal,
        status="scanning",
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return _scan_response(db, scan)


def update_scan(
    db: Session,
    user: User,
    scan_id: int,
    payload: TextbookScanUpdateRequest,
) -> TextbookScanResponse:
    scan = _get_owned_scan(db, user, scan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(scan, field, value)
    db.commit()
    db.refresh(scan)

    return _scan_response(db, scan)


def delete_scan(db: Session, user: User, scan_id: int) -> None:
    scan = _get_owned_scan(db, user, scan_id)
    db.execute(delete(ExtractedNote).where(ExtractedNote.scan_id == scan.id))
    db.execute(delete(TextbookPage).where(TextbookPage.scan_id == scan.id))
    db.delete(scan)
    db.commit()


def list_pages(db: Session, user: User) -> list[TextbookPageResponse]:
    rows = db.execute(
        select(TextbookPage, TextbookScan.title)
        .join(TextbookScan, TextbookScan.id == TextbookPage.scan_id)
        .where(TextbookPage.owner_id == user.id)
        .order_by(TextbookPage.updated_at.desc(), TextbookPage.page_number.asc())
    ).all()

    return [_page_response(db, page, scan_title) for page, scan_title in rows]


def create_page(
    db: Session,
    user: User,
    payload: TextbookPageCreateRequest,
) -> TextbookPageResponse:
    scan = _get_owned_scan(db, user, payload.scan_id)
    page = TextbookPage(
        owner_id=user.id,
        scan_id=scan.id,
        page_number=payload.page_number,
        title=payload.title,
        page_text=payload.page_text,
        status="captured",
    )
    db.add(page)
    db.commit()
    db.refresh(page)

    return _page_response(db, page, scan.title)


def update_page(
    db: Session,
    user: User,
    page_id: int,
    payload: TextbookPageUpdateRequest,
) -> TextbookPageResponse:
    page = _get_owned_page(db, user, page_id)
    scan = _get_owned_scan(db, user, page.scan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(page, field, value)
    db.commit()
    db.refresh(page)

    return _page_response(db, page, scan.title)


def delete_page(db: Session, user: User, page_id: int) -> None:
    page = _get_owned_page(db, user, page_id)
    db.execute(delete(ExtractedNote).where(ExtractedNote.page_id == page.id))
    db.delete(page)
    db.commit()


def list_notes(db: Session, user: User) -> list[ExtractedNoteResponse]:
    rows = db.execute(
        select(ExtractedNote, TextbookScan.title, TextbookPage.page_number)
        .join(TextbookScan, TextbookScan.id == ExtractedNote.scan_id)
        .join(TextbookPage, TextbookPage.id == ExtractedNote.page_id)
        .where(ExtractedNote.owner_id == user.id)
        .order_by(ExtractedNote.created_at.desc(), ExtractedNote.heading.asc())
    ).all()

    return [
        _note_response(note, scan_title, page_number)
        for note, scan_title, page_number in rows
    ]


def create_note(
    db: Session,
    user: User,
    payload: ExtractedNoteCreateRequest,
) -> ExtractedNoteResponse:
    scan = _get_owned_scan(db, user, payload.scan_id)
    page = _get_owned_page(db, user, payload.page_id)
    if page.scan_id != scan.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Textbook page must belong to the selected scan.",
        )

    note = ExtractedNote(
        owner_id=user.id,
        scan_id=scan.id,
        page_id=page.id,
        heading=payload.heading,
        key_points=payload.key_points,
        summary=payload.summary,
        note_type=payload.note_type,
    )
    page.status = "extracted"
    if scan.status == "scanning":
        scan.status = "extracting"
    db.add(note)
    db.commit()
    db.refresh(note)

    return _note_response(note, scan.title, page.page_number)


def get_review(db: Session, user: User) -> SmartTextbookScannerReviewResponse:
    scans = list(
        db.execute(select(TextbookScan).where(TextbookScan.owner_id == user.id))
        .scalars()
        .all()
    )
    pages = list(
        db.execute(select(TextbookPage).where(TextbookPage.owner_id == user.id))
        .scalars()
        .all()
    )
    extracted_page_count = len([page for page in pages if page.status == "extracted"])

    return SmartTextbookScannerReviewResponse(
        active_scan_count=len([scan for scan in scans if scan.status != "reviewed"]),
        reviewed_scan_count=len([scan for scan in scans if scan.status == "reviewed"]),
        total_page_count=len(pages),
        extracted_page_count=extracted_page_count,
        total_note_count=_count_notes(db, owner_id=user.id),
        extraction_rate=_rate(len(pages), extracted_page_count),
        recent_notes=list_notes(db, user)[:5],
    )


def get_dashboard(db: Session, user: User) -> SmartTextbookScannerDashboardResponse:
    return SmartTextbookScannerDashboardResponse(
        scans=list_scans(db, user),
        pages=list_pages(db, user),
        notes=list_notes(db, user),
        review=get_review(db, user),
    )
