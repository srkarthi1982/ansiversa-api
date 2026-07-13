from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

StudentStatus = Literal["active", "inactive", "graduated", "transferred", "withdrawn"]
ClassStatus = Literal["active", "upcoming", "completed", "archived"]
EnrollmentStatus = Literal["active", "removed"]
AttendanceStatus = Literal["present", "absent", "late", "excused", "remote", "not_recorded"]


def _normalize_text(value: object) -> object:
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None
    return value


class SchoolStudentCreateRequest(BaseModel):
    admission_number: str = Field(alias="admissionNumber", min_length=1, max_length=80)
    full_name: str = Field(alias="fullName", min_length=1, max_length=180)
    date_of_birth: str | None = Field(default=None, alias="dateOfBirth", max_length=40)
    gender: str | None = Field(default=None, max_length=40)
    guardian_name: str | None = Field(default=None, alias="guardianName", max_length=180)
    guardian_phone: str | None = Field(default=None, alias="guardianPhone", max_length=80)
    guardian_email: str | None = Field(default=None, alias="guardianEmail", max_length=180)
    address: str | None = Field(default=None, max_length=5000)
    admission_date: str | None = Field(default=None, alias="admissionDate", max_length=40)
    status: StudentStatus = "active"
    emergency_contact: str | None = Field(default=None, alias="emergencyContact", max_length=180)
    support_note: str | None = Field(default=None, alias="supportNote", max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SchoolStudentUpdateRequest(SchoolStudentCreateRequest):
    admission_number: str | None = Field(default=None, alias="admissionNumber", min_length=1, max_length=80)
    full_name: str | None = Field(default=None, alias="fullName", min_length=1, max_length=180)
    status: StudentStatus | None = None


class SchoolClassCreateRequest(BaseModel):
    class_name: str = Field(alias="className", min_length=1, max_length=160)
    grade_level: str | None = Field(default=None, alias="gradeLevel", max_length=80)
    section: str | None = Field(default=None, max_length=80)
    academic_year: str = Field(alias="academicYear", min_length=1, max_length=40)
    class_teacher: str | None = Field(default=None, alias="classTeacher", max_length=180)
    room: str | None = Field(default=None, max_length=80)
    capacity: int = Field(default=0, ge=0, le=10000)
    status: ClassStatus = "active"
    schedule_note: str | None = Field(default=None, alias="scheduleNote", max_length=5000)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SchoolClassUpdateRequest(SchoolClassCreateRequest):
    class_name: str | None = Field(default=None, alias="className", min_length=1, max_length=160)
    academic_year: str | None = Field(default=None, alias="academicYear", min_length=1, max_length=40)
    capacity: int | None = Field(default=None, ge=0, le=10000)
    status: ClassStatus | None = None


class SchoolEnrollmentCreateRequest(BaseModel):
    class_id: str = Field(alias="classId", max_length=36)
    student_id: str = Field(alias="studentId", max_length=36)
    enrolled_at: str | None = Field(default=None, alias="enrolledAt", max_length=40)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SchoolAttendanceCreateRequest(BaseModel):
    class_id: str = Field(alias="classId", max_length=36)
    student_id: str = Field(alias="studentId", max_length=36)
    attendance_date: str = Field(alias="attendanceDate", min_length=1, max_length=40)
    status: AttendanceStatus = "present"
    arrival_time: str | None = Field(default=None, alias="arrivalTime", max_length=40)
    reason: str | None = Field(default=None, max_length=5000)
    recorded_by: str | None = Field(default=None, alias="recordedBy", max_length=180)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SchoolAttendanceUpdateRequest(BaseModel):
    attendance_date: str | None = Field(default=None, alias="attendanceDate", min_length=1, max_length=40)
    status: AttendanceStatus | None = None
    arrival_time: str | None = Field(default=None, alias="arrivalTime", max_length=40)
    reason: str | None = Field(default=None, max_length=5000)
    recorded_by: str | None = Field(default=None, alias="recordedBy", max_length=180)
    notes: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return _normalize_text(value)


class SchoolEnrollmentResponse(BaseModel):
    id: str
    class_id: str = Field(serialization_alias="classId")
    class_name: str = Field(serialization_alias="className")
    student_id: str = Field(serialization_alias="studentId")
    student_name: str = Field(serialization_alias="studentName")
    admission_number: str = Field(serialization_alias="admissionNumber")
    status: EnrollmentStatus
    enrolled_at: str | None = Field(serialization_alias="enrolledAt")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SchoolStudentSummaryResponse(BaseModel):
    id: str
    admission_number: str = Field(serialization_alias="admissionNumber")
    full_name: str = Field(serialization_alias="fullName")
    date_of_birth: str | None = Field(serialization_alias="dateOfBirth")
    gender: str | None
    guardian_name: str | None = Field(serialization_alias="guardianName")
    guardian_phone: str | None = Field(serialization_alias="guardianPhone")
    guardian_email: str | None = Field(serialization_alias="guardianEmail")
    admission_date: str | None = Field(serialization_alias="admissionDate")
    current_class_id: str | None = Field(serialization_alias="currentClassId")
    current_class_name: str | None = Field(serialization_alias="currentClassName")
    status: StudentStatus
    emergency_contact: str | None = Field(serialization_alias="emergencyContact")
    support_note_preview: str | None = Field(serialization_alias="supportNotePreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SchoolStudentDetailResponse(SchoolStudentSummaryResponse):
    address: str | None
    support_note: str | None = Field(serialization_alias="supportNote")
    notes: str | None


class SchoolClassSummaryResponse(BaseModel):
    id: str
    class_name: str = Field(serialization_alias="className")
    grade_level: str | None = Field(serialization_alias="gradeLevel")
    section: str | None
    academic_year: str = Field(serialization_alias="academicYear")
    class_teacher: str | None = Field(serialization_alias="classTeacher")
    room: str | None
    capacity: int
    status: ClassStatus
    enrolled_count: int = Field(serialization_alias="enrolledCount")
    available_capacity: int = Field(serialization_alias="availableCapacity")
    schedule_note_preview: str | None = Field(serialization_alias="scheduleNotePreview")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    enrollments: list[SchoolEnrollmentResponse]
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SchoolClassDetailResponse(SchoolClassSummaryResponse):
    schedule_note: str | None = Field(serialization_alias="scheduleNote")
    notes: str | None


class SchoolAttendanceSummaryResponse(BaseModel):
    id: str
    class_id: str = Field(serialization_alias="classId")
    class_name: str = Field(serialization_alias="className")
    student_id: str = Field(serialization_alias="studentId")
    student_name: str = Field(serialization_alias="studentName")
    admission_number: str = Field(serialization_alias="admissionNumber")
    attendance_date: str = Field(serialization_alias="attendanceDate")
    status: AttendanceStatus
    arrival_time: str | None = Field(serialization_alias="arrivalTime")
    reason_preview: str | None = Field(serialization_alias="reasonPreview")
    recorded_by: str | None = Field(serialization_alias="recordedBy")
    notes_preview: str | None = Field(serialization_alias="notesPreview")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class SchoolAttendanceDetailResponse(SchoolAttendanceSummaryResponse):
    reason: str | None
    notes: str | None


class SchoolBreakdownResponse(BaseModel):
    label: str
    count: int


class SchoolAttendanceRateResponse(BaseModel):
    rate: float
    present_like: int = Field(serialization_alias="presentLike")
    counted_records: int = Field(serialization_alias="countedRecords")
    basis: str


class SchoolDashboardResponse(BaseModel):
    students: list[SchoolStudentSummaryResponse]
    classes: list[SchoolClassSummaryResponse]
    attendance: list[SchoolAttendanceSummaryResponse]
    total_students: int = Field(serialization_alias="totalStudents")
    active_students: int = Field(serialization_alias="activeStudents")
    new_admissions: int = Field(serialization_alias="newAdmissions")
    inactive_students: int = Field(serialization_alias="inactiveStudents")
    total_classes: int = Field(serialization_alias="totalClasses")
    active_classes: int = Field(serialization_alias="activeClasses")
    total_enrollments: int = Field(serialization_alias="totalEnrollments")
    available_seats: int = Field(serialization_alias="availableSeats")
    present_count: int = Field(serialization_alias="presentCount")
    absent_count: int = Field(serialization_alias="absentCount")
    late_count: int = Field(serialization_alias="lateCount")
    attendance_rate: SchoolAttendanceRateResponse = Field(serialization_alias="attendanceRate")
    students_by_class: list[SchoolBreakdownResponse] = Field(serialization_alias="studentsByClass")
    students_by_status: list[SchoolBreakdownResponse] = Field(serialization_alias="studentsByStatus")
    attendance_by_class: list[SchoolBreakdownResponse] = Field(serialization_alias="attendanceByClass")
    monthly_attendance_activity: list[SchoolBreakdownResponse] = Field(serialization_alias="monthlyAttendanceActivity")
    recent_admissions: list[SchoolStudentSummaryResponse] = Field(serialization_alias="recentAdmissions")
    recent_activity: list[SchoolAttendanceSummaryResponse] = Field(serialization_alias="recentActivity")
