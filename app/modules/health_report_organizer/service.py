from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.health_report_organizer import repository
from app.modules.health_report_organizer.models import (
    HealthReport,
    HealthReportAttachment,
    HealthReportCategory,
    HealthReportFacility,
    HealthReportNote,
)
from app.modules.health_report_organizer.schemas import (
    AttachmentCreateRequest,
    AttachmentDetailResponse,
    AttachmentSummaryResponse,
    AttachmentUpdateRequest,
    CategoryCreateRequest,
    CategoryDetailResponse,
    CategorySummaryResponse,
    CategoryUpdateRequest,
    FacilityCreateRequest,
    FacilityDetailResponse,
    FacilitySummaryResponse,
    FacilityUpdateRequest,
    HealthReportOrganizerDashboardResponse,
    HealthReportNoteCreateRequest,
    HealthReportNoteDetailResponse,
    HealthReportNoteSummaryResponse,
    HealthReportNoteUpdateRequest,
    ReportCreateRequest,
    ReportDetailResponse,
    ReportSummaryResponse,
    ReportUpdateRequest,
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


def _get_owned_category(db: Session, user: User, category_id: str) -> HealthReportCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Category was not found.")
    return category


def _get_owned_facility(db: Session, user: User, facility_id: str) -> HealthReportFacility:
    facility = repository.get_facility(db, facility_id)
    if not facility or facility.owner_id != user.id:
        _not_found("Facility was not found.")
    return facility


def _get_owned_report(db: Session, user: User, report_id: str) -> HealthReport:
    report = repository.get_report(db, report_id)
    if not report or report.owner_id != user.id:
        _not_found("Report was not found.")
    return report


def _get_owned_attachment(db: Session, user: User, attachment_id: str) -> HealthReportAttachment:
    attachment = repository.get_attachment(db, attachment_id)
    if not attachment or attachment.owner_id != user.id:
        _not_found("Attachment was not found.")
    return attachment


def _get_owned_note(db: Session, user: User, note_id: str) -> HealthReportNote:
    note = repository.get_note(db, note_id)
    if not note or note.owner_id != user.id:
        _not_found("Note was not found.")
    return note


def _category_summary(category: HealthReportCategory) -> CategorySummaryResponse:
    return CategorySummaryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        description_preview=_preview(category.description),
        status=category.status,
        report_count=len(category.reports),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _facility_summary(facility: HealthReportFacility) -> FacilitySummaryResponse:
    return FacilitySummaryResponse(
        id=facility.id,
        name=facility.name,
        facility_type=facility.facility_type,
        phone=facility.phone,
        website=facility.website,
        address_preview=_preview(facility.address),
        notes_preview=_preview(facility.notes),
        status=facility.status,
        report_count=len(facility.reports),
        created_at=facility.created_at,
        updated_at=facility.updated_at,
    )


def _report_summary(report: HealthReport) -> ReportSummaryResponse:
    return ReportSummaryResponse(
        id=report.id,
        category_id=report.category_id,
        category_name=report.category.name if report.category else None,
        facility_id=report.facility_id,
        facility_name=report.facility.name if report.facility else None,
        title=report.title,
        report_type=report.report_type,
        report_date=report.report_date,
        patient_name=report.patient_name,
        doctor_name=report.doctor_name,
        summary_preview=_preview(report.summary),
        status=report.status,
        priority=report.priority,
        attachment_count=len(report.attachments),
        note_count=len(report.notes),
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def _attachment_summary(attachment: HealthReportAttachment) -> AttachmentSummaryResponse:
    return AttachmentSummaryResponse(
        id=attachment.id,
        report_id=attachment.report_id,
        report_title=attachment.report.title,
        file_name=attachment.file_name,
        file_type=attachment.file_type,
        source=attachment.source,
        reference_url=attachment.reference_url,
        storage_location=attachment.storage_location,
        notes_preview=_preview(attachment.notes),
        status=attachment.status,
        created_at=attachment.created_at,
        updated_at=attachment.updated_at,
    )


def _note_summary(note: HealthReportNote) -> HealthReportNoteSummaryResponse:
    return HealthReportNoteSummaryResponse(
        id=note.id,
        report_id=note.report_id,
        report_title=note.report.title,
        note_date=note.note_date,
        title=note.title,
        body_preview=_preview(note.body),
        category=note.category,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _category_detail(category: HealthReportCategory) -> CategoryDetailResponse:
    return CategoryDetailResponse(**_category_summary(category).model_dump(), description=category.description)


def _facility_detail(facility: HealthReportFacility) -> FacilityDetailResponse:
    return FacilityDetailResponse(**_facility_summary(facility).model_dump(), address=facility.address, notes=facility.notes)


def _report_detail(report: HealthReport) -> ReportDetailResponse:
    attachments = sorted(report.attachments, key=lambda item: (item.updated_at, item.file_name), reverse=True)
    notes = sorted(report.notes, key=lambda item: (item.note_date, item.updated_at), reverse=True)
    return ReportDetailResponse(
        **_report_summary(report).model_dump(),
        summary=report.summary,
        attachments=[_attachment_summary(attachment) for attachment in attachments],
        notes=[_note_summary(note) for note in notes],
    )


def _attachment_detail(attachment: HealthReportAttachment) -> AttachmentDetailResponse:
    return AttachmentDetailResponse(**_attachment_summary(attachment).model_dump(), notes=attachment.notes)


def _note_detail(note: HealthReportNote) -> HealthReportNoteDetailResponse:
    return HealthReportNoteDetailResponse(**_note_summary(note).model_dump(), body=note.body)


def _validate_optional_parent(db: Session, user: User, category_id: str | None, facility_id: str | None) -> None:
    if category_id:
        _get_owned_category(db, user, category_id)
    if facility_id:
        _get_owned_facility(db, user, facility_id)


def list_categories(db: Session, user: User) -> list[CategorySummaryResponse]:
    return [_category_summary(category) for category in repository.list_categories(db, user.id)]


def create_category(db: Session, user: User, payload: CategoryCreateRequest) -> CategoryDetailResponse:
    category = HealthReportCategory(owner_id=user.id, **payload.model_dump())
    repository.add(db, category)
    db.commit()
    db.refresh(category)
    return _category_detail(category)


def get_category(db: Session, user: User, category_id: str) -> CategoryDetailResponse:
    return _category_detail(_get_owned_category(db, user, category_id))


def update_category(db: Session, user: User, category_id: str, payload: CategoryUpdateRequest) -> CategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return _category_detail(category)


def delete_category(db: Session, user: User, category_id: str) -> None:
    category = _get_owned_category(db, user, category_id)
    repository.delete_record(db, category)
    db.commit()


def list_facilities(db: Session, user: User) -> list[FacilitySummaryResponse]:
    return [_facility_summary(facility) for facility in repository.list_facilities(db, user.id)]


def create_facility(db: Session, user: User, payload: FacilityCreateRequest) -> FacilityDetailResponse:
    facility = HealthReportFacility(owner_id=user.id, **payload.model_dump())
    repository.add(db, facility)
    db.commit()
    db.refresh(facility)
    return _facility_detail(facility)


def get_facility(db: Session, user: User, facility_id: str) -> FacilityDetailResponse:
    return _facility_detail(_get_owned_facility(db, user, facility_id))


def update_facility(db: Session, user: User, facility_id: str, payload: FacilityUpdateRequest) -> FacilityDetailResponse:
    facility = _get_owned_facility(db, user, facility_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(facility, field, value)
    db.commit()
    db.refresh(facility)
    return _facility_detail(facility)


def delete_facility(db: Session, user: User, facility_id: str) -> None:
    facility = _get_owned_facility(db, user, facility_id)
    repository.delete_record(db, facility)
    db.commit()


def list_reports(db: Session, user: User) -> list[ReportSummaryResponse]:
    return [_report_summary(report) for report in repository.list_reports(db, user.id)]


def create_report(db: Session, user: User, payload: ReportCreateRequest) -> ReportDetailResponse:
    data = payload.model_dump()
    _validate_optional_parent(db, user, data.get("category_id"), data.get("facility_id"))
    report = HealthReport(owner_id=user.id, **data)
    repository.add(db, report)
    db.commit()
    db.refresh(report)
    return _report_detail(report)


def get_report(db: Session, user: User, report_id: str) -> ReportDetailResponse:
    return _report_detail(_get_owned_report(db, user, report_id))


def update_report(db: Session, user: User, report_id: str, payload: ReportUpdateRequest) -> ReportDetailResponse:
    report = _get_owned_report(db, user, report_id)
    data = payload.model_dump(exclude_unset=True)
    _validate_optional_parent(db, user, data.get("category_id"), data.get("facility_id"))
    for field, value in data.items():
        setattr(report, field, value)
    db.commit()
    db.refresh(report)
    return _report_detail(report)


def delete_report(db: Session, user: User, report_id: str) -> None:
    report = _get_owned_report(db, user, report_id)
    repository.delete_record(db, report)
    db.commit()


def list_attachments(db: Session, user: User) -> list[AttachmentSummaryResponse]:
    return [_attachment_summary(attachment) for attachment in repository.list_attachments(db, user.id)]


def create_attachment(db: Session, user: User, payload: AttachmentCreateRequest) -> AttachmentDetailResponse:
    data = payload.model_dump()
    _get_owned_report(db, user, data["report_id"])
    attachment = HealthReportAttachment(owner_id=user.id, **data)
    repository.add(db, attachment)
    db.commit()
    db.refresh(attachment)
    return _attachment_detail(attachment)


def get_attachment(db: Session, user: User, attachment_id: str) -> AttachmentDetailResponse:
    return _attachment_detail(_get_owned_attachment(db, user, attachment_id))


def update_attachment(db: Session, user: User, attachment_id: str, payload: AttachmentUpdateRequest) -> AttachmentDetailResponse:
    attachment = _get_owned_attachment(db, user, attachment_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(attachment, field, value)
    db.commit()
    db.refresh(attachment)
    return _attachment_detail(attachment)


def delete_attachment(db: Session, user: User, attachment_id: str) -> None:
    attachment = _get_owned_attachment(db, user, attachment_id)
    repository.delete_record(db, attachment)
    db.commit()


def list_notes(db: Session, user: User) -> list[HealthReportNoteSummaryResponse]:
    return [_note_summary(note) for note in repository.list_notes(db, user.id)]


def create_note(db: Session, user: User, payload: HealthReportNoteCreateRequest) -> HealthReportNoteDetailResponse:
    data = payload.model_dump()
    _get_owned_report(db, user, data["report_id"])
    note = HealthReportNote(owner_id=user.id, **data)
    repository.add(db, note)
    db.commit()
    db.refresh(note)
    return _note_detail(note)


def get_note(db: Session, user: User, note_id: str) -> HealthReportNoteDetailResponse:
    return _note_detail(_get_owned_note(db, user, note_id))


def update_note(db: Session, user: User, note_id: str, payload: HealthReportNoteUpdateRequest) -> HealthReportNoteDetailResponse:
    note = _get_owned_note(db, user, note_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return _note_detail(note)


def delete_note(db: Session, user: User, note_id: str) -> None:
    note = _get_owned_note(db, user, note_id)
    repository.delete_record(db, note)
    db.commit()


def get_dashboard(db: Session, user: User) -> HealthReportOrganizerDashboardResponse:
    reports = list_reports(db, user)
    categories = list_categories(db, user)
    facilities = list_facilities(db, user)
    attachments = list_attachments(db, user)
    notes = list_notes(db, user)
    return HealthReportOrganizerDashboardResponse(
        reports=reports,
        categories=categories,
        facilities=facilities,
        attachments=attachments,
        notes=notes,
        report_count=len(reports),
        reviewed_count=sum(1 for report in reports if report.status == "reviewed"),
        follow_up_count=sum(1 for report in reports if report.status == "followUp"),
        attachment_count=len(attachments),
        recent_reports=reports[:5],
        recent_notes=notes[:5],
    )
