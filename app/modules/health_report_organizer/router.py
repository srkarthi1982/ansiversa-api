from fastapi import APIRouter, Response, status

from app.modules.health_report_organizer import service
from app.modules.health_report_organizer.dependencies import (
    CurrentHealthReportOrganizerUser,
    HealthReportOrganizerDB,
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

router = APIRouter()


@router.get("/dashboard", response_model=HealthReportOrganizerDashboardResponse)
def get_dashboard(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_dashboard(db, current_user)


@router.get("/reports", response_model=list[ReportSummaryResponse])
def list_reports(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.list_reports(db, current_user)


@router.post("/reports", response_model=ReportDetailResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: ReportCreateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.create_report(db, current_user, payload)


@router.get("/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(report_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_report(db, current_user, report_id)


@router.put("/reports/{report_id}", response_model=ReportDetailResponse)
def update_report(report_id: str, payload: ReportUpdateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.update_report(db, current_user, report_id, payload)


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    service.delete_report(db, current_user, report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=list[CategorySummaryResponse])
def list_categories(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=CategoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.create_category(db, current_user, payload)


@router.get("/categories/{category_id}", response_model=CategoryDetailResponse)
def get_category(category_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_category(db, current_user, category_id)


@router.put("/categories/{category_id}", response_model=CategoryDetailResponse)
def update_category(category_id: str, payload: CategoryUpdateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/facilities", response_model=list[FacilitySummaryResponse])
def list_facilities(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.list_facilities(db, current_user)


@router.post("/facilities", response_model=FacilityDetailResponse, status_code=status.HTTP_201_CREATED)
def create_facility(payload: FacilityCreateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.create_facility(db, current_user, payload)


@router.get("/facilities/{facility_id}", response_model=FacilityDetailResponse)
def get_facility(facility_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_facility(db, current_user, facility_id)


@router.put("/facilities/{facility_id}", response_model=FacilityDetailResponse)
def update_facility(facility_id: str, payload: FacilityUpdateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.update_facility(db, current_user, facility_id, payload)


@router.delete("/facilities/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(facility_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    service.delete_facility(db, current_user, facility_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/attachments", response_model=list[AttachmentSummaryResponse])
def list_attachments(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.list_attachments(db, current_user)


@router.post("/attachments", response_model=AttachmentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_attachment(payload: AttachmentCreateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.create_attachment(db, current_user, payload)


@router.get("/attachments/{attachment_id}", response_model=AttachmentDetailResponse)
def get_attachment(attachment_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_attachment(db, current_user, attachment_id)


@router.put("/attachments/{attachment_id}", response_model=AttachmentDetailResponse)
def update_attachment(attachment_id: str, payload: AttachmentUpdateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.update_attachment(db, current_user, attachment_id, payload)


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(attachment_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    service.delete_attachment(db, current_user, attachment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notes", response_model=list[HealthReportNoteSummaryResponse])
def list_notes(db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.list_notes(db, current_user)


@router.post("/notes", response_model=HealthReportNoteDetailResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: HealthReportNoteCreateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.create_note(db, current_user, payload)


@router.get("/notes/{note_id}", response_model=HealthReportNoteDetailResponse)
def get_note(note_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.get_note(db, current_user, note_id)


@router.put("/notes/{note_id}", response_model=HealthReportNoteDetailResponse)
def update_note(note_id: str, payload: HealthReportNoteUpdateRequest, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    return service.update_note(db, current_user, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, db: HealthReportOrganizerDB, current_user: CurrentHealthReportOrganizerUser):
    service.delete_note(db, current_user, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
