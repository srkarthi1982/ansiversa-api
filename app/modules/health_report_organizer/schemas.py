from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ReportStatus = Literal["new", "reviewed", "followUp", "archived"]
ReportPriority = Literal["routine", "important", "urgent"]
ReportType = Literal["lab", "imaging", "prescription", "discharge", "vaccination", "consultation", "other"]
RecordStatus = Literal["active", "archived"]
FacilityType = Literal["clinic", "hospital", "lab", "imaging", "pharmacy", "other"]
AttachmentStatus = Literal["available", "requested", "archived"]
NoteCategory = Literal["general", "question", "followUp", "result", "billing"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    color: str | None = Field(default=None, max_length=40)
    description: str | None = Field(default=None, max_length=2000)
    status: RecordStatus = "active"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CategoryUpdateRequest(CategoryCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=140)
    status: RecordStatus | None = None


class FacilityCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    facility_type: FacilityType = Field(default="clinic", alias="facilityType")
    phone: str | None = Field(default=None, max_length=80)
    website: str | None = Field(default=None, max_length=240)
    address: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=3000)
    status: RecordStatus = "active"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class FacilityUpdateRequest(FacilityCreateRequest):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    facility_type: FacilityType | None = Field(default=None, alias="facilityType")
    status: RecordStatus | None = None


class ReportCreateRequest(BaseModel):
    category_id: str | None = Field(default=None, alias="categoryId", max_length=36)
    facility_id: str | None = Field(default=None, alias="facilityId", max_length=36)
    title: str = Field(min_length=1, max_length=180)
    report_type: ReportType = Field(default="lab", alias="reportType")
    report_date: str = Field(alias="reportDate", min_length=1, max_length=40)
    patient_name: str | None = Field(default=None, alias="patientName", max_length=140)
    doctor_name: str | None = Field(default=None, alias="doctorName", max_length=140)
    summary: str | None = Field(default=None, max_length=4000)
    status: ReportStatus = "new"
    priority: ReportPriority = "routine"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class ReportUpdateRequest(ReportCreateRequest):
    category_id: str | None = Field(default=None, alias="categoryId", max_length=36)
    facility_id: str | None = Field(default=None, alias="facilityId", max_length=36)
    title: str | None = Field(default=None, min_length=1, max_length=180)
    report_type: ReportType | None = Field(default=None, alias="reportType")
    report_date: str | None = Field(default=None, alias="reportDate", min_length=1, max_length=40)
    status: ReportStatus | None = None
    priority: ReportPriority | None = None


class AttachmentCreateRequest(BaseModel):
    report_id: str = Field(alias="reportId", min_length=1, max_length=36)
    file_name: str = Field(alias="fileName", min_length=1, max_length=220)
    file_type: str | None = Field(default=None, alias="fileType", max_length=80)
    source: str | None = Field(default=None, max_length=120)
    reference_url: str | None = Field(default=None, alias="referenceUrl", max_length=500)
    storage_location: str | None = Field(default=None, alias="storageLocation", max_length=220)
    notes: str | None = Field(default=None, max_length=3000)
    status: AttachmentStatus = "available"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class AttachmentUpdateRequest(BaseModel):
    file_name: str | None = Field(default=None, alias="fileName", min_length=1, max_length=220)
    file_type: str | None = Field(default=None, alias="fileType", max_length=80)
    source: str | None = Field(default=None, max_length=120)
    reference_url: str | None = Field(default=None, alias="referenceUrl", max_length=500)
    storage_location: str | None = Field(default=None, alias="storageLocation", max_length=220)
    notes: str | None = Field(default=None, max_length=3000)
    status: AttachmentStatus | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class HealthReportNoteCreateRequest(BaseModel):
    report_id: str = Field(alias="reportId", min_length=1, max_length=36)
    note_date: str = Field(alias="noteDate", min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=4000)
    category: NoteCategory = "general"

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class HealthReportNoteUpdateRequest(BaseModel):
    note_date: str | None = Field(default=None, alias="noteDate", min_length=1, max_length=40)
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=4000)
    category: NoteCategory | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class CategorySummaryResponse(BaseModel):
    id: str
    name: str
    color: str | None
    description_preview: str | None = Field(serialization_alias="descriptionPreview")
    status: RecordStatus
    report_count: int = Field(serialization_alias="reportCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class FacilitySummaryResponse(BaseModel):
    id: str
    name: str
    facility_type: FacilityType = Field(serialization_alias="facilityType")
    phone: str | None
    website: str | None
    address_preview: str | None = Field(serialization_alias="addressPreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    status: RecordStatus
    report_count: int = Field(serialization_alias="reportCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ReportSummaryResponse(BaseModel):
    id: str
    category_id: str | None = Field(serialization_alias="categoryId")
    category_name: str | None = Field(serialization_alias="categoryName")
    facility_id: str | None = Field(serialization_alias="facilityId")
    facility_name: str | None = Field(serialization_alias="facilityName")
    title: str
    report_type: ReportType = Field(serialization_alias="reportType")
    report_date: str = Field(serialization_alias="reportDate")
    patient_name: str | None = Field(serialization_alias="patientName")
    doctor_name: str | None = Field(serialization_alias="doctorName")
    summary_preview: str | None = Field(serialization_alias="summaryPreview")
    status: ReportStatus
    priority: ReportPriority
    attachment_count: int = Field(serialization_alias="attachmentCount")
    note_count: int = Field(serialization_alias="noteCount")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class AttachmentSummaryResponse(BaseModel):
    id: str
    report_id: str = Field(serialization_alias="reportId")
    report_title: str = Field(serialization_alias="reportTitle")
    file_name: str = Field(serialization_alias="fileName")
    file_type: str | None = Field(serialization_alias="fileType")
    source: str | None
    reference_url: str | None = Field(serialization_alias="referenceUrl")
    storage_location: str | None = Field(serialization_alias="storageLocation")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    status: AttachmentStatus
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class HealthReportNoteSummaryResponse(BaseModel):
    id: str
    report_id: str = Field(serialization_alias="reportId")
    report_title: str = Field(serialization_alias="reportTitle")
    note_date: str = Field(serialization_alias="noteDate")
    title: str
    body_preview: str | None = Field(serialization_alias="bodyPreview")
    category: NoteCategory
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CategoryDetailResponse(CategorySummaryResponse):
    description: str | None


class FacilityDetailResponse(FacilitySummaryResponse):
    address: str | None
    notes: str | None


class ReportDetailResponse(ReportSummaryResponse):
    summary: str | None
    attachments: list[AttachmentSummaryResponse]
    notes: list[HealthReportNoteSummaryResponse]


class AttachmentDetailResponse(AttachmentSummaryResponse):
    notes: str | None


class HealthReportNoteDetailResponse(HealthReportNoteSummaryResponse):
    body: str | None


class HealthReportOrganizerDashboardResponse(BaseModel):
    reports: list[ReportSummaryResponse]
    categories: list[CategorySummaryResponse]
    facilities: list[FacilitySummaryResponse]
    attachments: list[AttachmentSummaryResponse]
    notes: list[HealthReportNoteSummaryResponse]
    report_count: int = Field(serialization_alias="reportCount")
    reviewed_count: int = Field(serialization_alias="reviewedCount")
    follow_up_count: int = Field(serialization_alias="followUpCount")
    attachment_count: int = Field(serialization_alias="attachmentCount")
    recent_reports: list[ReportSummaryResponse] = Field(serialization_alias="recentReports")
    recent_notes: list[HealthReportNoteSummaryResponse] = Field(serialization_alias="recentNotes")
