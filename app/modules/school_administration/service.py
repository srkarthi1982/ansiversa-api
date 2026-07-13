from collections import Counter, defaultdict
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.school_administration import repository
from app.modules.school_administration.models import SchoolAttendance, SchoolClass, SchoolEnrollment, SchoolStudent
from app.modules.school_administration.schemas import (
    SchoolAttendanceCreateRequest,
    SchoolAttendanceDetailResponse,
    SchoolAttendanceRateResponse,
    SchoolAttendanceSummaryResponse,
    SchoolAttendanceUpdateRequest,
    SchoolBreakdownResponse,
    SchoolClassCreateRequest,
    SchoolClassDetailResponse,
    SchoolClassSummaryResponse,
    SchoolClassUpdateRequest,
    SchoolDashboardResponse,
    SchoolEnrollmentCreateRequest,
    SchoolEnrollmentResponse,
    SchoolStudentCreateRequest,
    SchoolStudentDetailResponse,
    SchoolStudentSummaryResponse,
    SchoolStudentUpdateRequest,
)

PREVIEW_LENGTH = 180
ATTENDANCE_BASIS = "Present, late, remote, absent, and excused records are counted. Not recorded records are excluded."


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _conflict(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def _get_owned_student(db: Session, user: User, student_id: str) -> SchoolStudent:
    student = repository.get_student(db, student_id)
    if not student or student.owner_id != user.id:
        _not_found("Student was not found.")
    return student


def _get_owned_class(db: Session, user: User, class_id: str) -> SchoolClass:
    school_class = repository.get_class(db, class_id)
    if not school_class or school_class.owner_id != user.id:
        _not_found("Class was not found.")
    return school_class


def _get_owned_enrollment(db: Session, user: User, enrollment_id: str) -> SchoolEnrollment:
    enrollment = repository.get_enrollment(db, enrollment_id)
    if not enrollment or enrollment.owner_id != user.id:
        _not_found("Enrollment was not found.")
    return enrollment


def _get_owned_attendance(db: Session, user: User, attendance_id: str) -> SchoolAttendance:
    attendance = repository.get_attendance(db, attendance_id)
    if not attendance or attendance.owner_id != user.id:
        _not_found("Attendance record was not found.")
    return attendance


def _active_enrollments(enrollments: list[SchoolEnrollment]) -> list[SchoolEnrollment]:
    return [enrollment for enrollment in enrollments if enrollment.status == "active"]


def _current_class(student: SchoolStudent) -> SchoolEnrollment | None:
    active = _active_enrollments(student.enrollments)
    if not active:
        return None
    return sorted(active, key=lambda item: item.updated_at, reverse=True)[0]


def _enrollment_response(enrollment: SchoolEnrollment) -> SchoolEnrollmentResponse:
    return SchoolEnrollmentResponse(
        id=enrollment.id,
        class_id=enrollment.class_id,
        class_name=enrollment.school_class.class_name if enrollment.school_class else "Class",
        student_id=enrollment.student_id,
        student_name=enrollment.student.full_name if enrollment.student else "Student",
        admission_number=enrollment.student.admission_number if enrollment.student else "",
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        notes_preview=_preview(enrollment.notes),
        created_at=enrollment.created_at,
        updated_at=enrollment.updated_at,
    )


def _student_summary(student: SchoolStudent) -> SchoolStudentSummaryResponse:
    current = _current_class(student)
    return SchoolStudentSummaryResponse(
        id=student.id,
        admission_number=student.admission_number,
        full_name=student.full_name,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        guardian_name=student.guardian_name,
        guardian_phone=student.guardian_phone,
        guardian_email=student.guardian_email,
        admission_date=student.admission_date,
        current_class_id=current.class_id if current else None,
        current_class_name=current.school_class.class_name if current and current.school_class else None,
        status=student.status,
        emergency_contact=student.emergency_contact,
        support_note_preview=_preview(student.support_note),
        notes_preview=_preview(student.notes),
        created_at=student.created_at,
        updated_at=student.updated_at,
    )


def _student_detail(student: SchoolStudent) -> SchoolStudentDetailResponse:
    return SchoolStudentDetailResponse(**_student_summary(student).model_dump(), address=student.address, support_note=student.support_note, notes=student.notes)


def _class_summary(school_class: SchoolClass) -> SchoolClassSummaryResponse:
    enrollments = [_enrollment_response(enrollment) for enrollment in _active_enrollments(school_class.enrollments)]
    enrolled_count = len(enrollments)
    available_capacity = max((school_class.capacity or 0) - enrolled_count, 0)
    return SchoolClassSummaryResponse(
        id=school_class.id,
        class_name=school_class.class_name,
        grade_level=school_class.grade_level,
        section=school_class.section,
        academic_year=school_class.academic_year,
        class_teacher=school_class.class_teacher,
        room=school_class.room,
        capacity=school_class.capacity,
        status=school_class.status,
        enrolled_count=enrolled_count,
        available_capacity=available_capacity,
        schedule_note_preview=_preview(school_class.schedule_note),
        notes_preview=_preview(school_class.notes),
        enrollments=enrollments,
        created_at=school_class.created_at,
        updated_at=school_class.updated_at,
    )


def _class_detail(school_class: SchoolClass) -> SchoolClassDetailResponse:
    return SchoolClassDetailResponse(**_class_summary(school_class).model_dump(), schedule_note=school_class.schedule_note, notes=school_class.notes)


def _attendance_summary(attendance: SchoolAttendance) -> SchoolAttendanceSummaryResponse:
    return SchoolAttendanceSummaryResponse(
        id=attendance.id,
        class_id=attendance.class_id,
        class_name=attendance.school_class.class_name if attendance.school_class else "Class",
        student_id=attendance.student_id,
        student_name=attendance.student.full_name if attendance.student else "Student",
        admission_number=attendance.student.admission_number if attendance.student else "",
        attendance_date=attendance.attendance_date,
        status=attendance.status,
        arrival_time=attendance.arrival_time,
        reason_preview=_preview(attendance.reason),
        recorded_by=attendance.recorded_by,
        notes_preview=_preview(attendance.notes),
        created_at=attendance.created_at,
        updated_at=attendance.updated_at,
    )


def _attendance_detail(attendance: SchoolAttendance) -> SchoolAttendanceDetailResponse:
    return SchoolAttendanceDetailResponse(**_attendance_summary(attendance).model_dump(), reason=attendance.reason, notes=attendance.notes)


def _assert_unique_admission(db: Session, user: User, admission_number: str, current_id: str | None = None) -> None:
    existing = repository.find_student_by_admission_number(db, user.id, admission_number)
    if existing and existing.id != current_id:
        _conflict("A student with this admission number already exists.")


def _assert_attendance_unique(db: Session, user: User, class_id: str, student_id: str, attendance_date: str, current_id: str | None = None) -> None:
    existing = repository.find_attendance(db, user.id, class_id, student_id, attendance_date)
    if existing and existing.id != current_id:
        _conflict("Attendance is already recorded for this student, class, and date.")


def _attendance_rate(records: list[SchoolAttendance]) -> SchoolAttendanceRateResponse:
    counted = [record for record in records if record.status != "not_recorded"]
    present_like = sum(1 for record in counted if record.status in {"present", "late", "remote"})
    rate = round((present_like / len(counted)) * 100, 1) if counted else 0
    return SchoolAttendanceRateResponse(rate=rate, present_like=present_like, counted_records=len(counted), basis=ATTENDANCE_BASIS)


def list_students(db: Session, user: User) -> list[SchoolStudentSummaryResponse]:
    return [_student_summary(student) for student in repository.list_students(db, user.id)]


def create_student(db: Session, user: User, payload: SchoolStudentCreateRequest) -> SchoolStudentDetailResponse:
    data = payload.model_dump()
    _assert_unique_admission(db, user, data["admission_number"])
    student = SchoolStudent(owner_id=user.id, **data)
    repository.add(db, student)
    db.commit()
    db.refresh(student)
    return _student_detail(student)


def get_student(db: Session, user: User, student_id: str) -> SchoolStudentDetailResponse:
    return _student_detail(_get_owned_student(db, user, student_id))


def update_student(db: Session, user: User, student_id: str, payload: SchoolStudentUpdateRequest) -> SchoolStudentDetailResponse:
    student = _get_owned_student(db, user, student_id)
    data = payload.model_dump(exclude_unset=True)
    if "admission_number" in data:
        _assert_unique_admission(db, user, data["admission_number"], student.id)
    for field, value in data.items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return _student_detail(student)


def duplicate_student(db: Session, user: User, student_id: str) -> SchoolStudentDetailResponse:
    source = _get_owned_student(db, user, student_id)
    admission_number = f"{source.admission_number}-copy"
    suffix = 2
    while repository.find_student_by_admission_number(db, user.id, admission_number):
        admission_number = f"{source.admission_number}-copy-{suffix}"
        suffix += 1
    copy = SchoolStudent(
        owner_id=user.id,
        admission_number=admission_number,
        full_name=f"{source.full_name} copy",
        date_of_birth=source.date_of_birth,
        gender=source.gender,
        guardian_name=source.guardian_name,
        guardian_phone=source.guardian_phone,
        guardian_email=source.guardian_email,
        address=source.address,
        admission_date=source.admission_date,
        status="active",
        emergency_contact=source.emergency_contact,
        support_note=source.support_note,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _student_detail(copy)


def delete_student(db: Session, user: User, student_id: str) -> None:
    student = _get_owned_student(db, user, student_id)
    repository.delete_record(db, student)
    db.commit()


def list_classes(db: Session, user: User) -> list[SchoolClassSummaryResponse]:
    return [_class_summary(school_class) for school_class in repository.list_classes(db, user.id)]


def create_class(db: Session, user: User, payload: SchoolClassCreateRequest) -> SchoolClassDetailResponse:
    school_class = SchoolClass(owner_id=user.id, **payload.model_dump())
    repository.add(db, school_class)
    db.commit()
    db.refresh(school_class)
    return _class_detail(school_class)


def get_class(db: Session, user: User, class_id: str) -> SchoolClassDetailResponse:
    return _class_detail(_get_owned_class(db, user, class_id))


def update_class(db: Session, user: User, class_id: str, payload: SchoolClassUpdateRequest) -> SchoolClassDetailResponse:
    school_class = _get_owned_class(db, user, class_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(school_class, field, value)
    db.commit()
    db.refresh(school_class)
    return _class_detail(school_class)


def duplicate_class(db: Session, user: User, class_id: str) -> SchoolClassDetailResponse:
    source = _get_owned_class(db, user, class_id)
    copy = SchoolClass(
        owner_id=user.id,
        class_name=f"{source.class_name} copy",
        grade_level=source.grade_level,
        section=source.section,
        academic_year=source.academic_year,
        class_teacher=source.class_teacher,
        room=source.room,
        capacity=source.capacity,
        status="upcoming",
        schedule_note=source.schedule_note,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _class_detail(copy)


def delete_class(db: Session, user: User, class_id: str) -> None:
    school_class = _get_owned_class(db, user, class_id)
    repository.delete_record(db, school_class)
    db.commit()


def create_enrollment(db: Session, user: User, payload: SchoolEnrollmentCreateRequest) -> SchoolEnrollmentResponse:
    data = payload.model_dump()
    _get_owned_class(db, user, data["class_id"])
    _get_owned_student(db, user, data["student_id"])
    existing = repository.find_active_enrollment(db, user.id, data["class_id"], data["student_id"])
    if existing:
        _conflict("This student is already actively enrolled in this class.")
    enrollment = SchoolEnrollment(owner_id=user.id, status="active", **data)
    repository.add(db, enrollment)
    db.commit()
    db.refresh(enrollment)
    return _enrollment_response(enrollment)


def delete_enrollment(db: Session, user: User, enrollment_id: str) -> None:
    enrollment = _get_owned_enrollment(db, user, enrollment_id)
    repository.delete_record(db, enrollment)
    db.commit()


def list_attendance(db: Session, user: User) -> list[SchoolAttendanceSummaryResponse]:
    return [_attendance_summary(attendance) for attendance in repository.list_attendance(db, user.id)]


def create_attendance(db: Session, user: User, payload: SchoolAttendanceCreateRequest) -> SchoolAttendanceDetailResponse:
    data = payload.model_dump()
    _get_owned_class(db, user, data["class_id"])
    _get_owned_student(db, user, data["student_id"])
    _assert_attendance_unique(db, user, data["class_id"], data["student_id"], data["attendance_date"])
    attendance = SchoolAttendance(owner_id=user.id, **data)
    repository.add(db, attendance)
    db.commit()
    db.refresh(attendance)
    return _attendance_detail(attendance)


def get_attendance(db: Session, user: User, attendance_id: str) -> SchoolAttendanceDetailResponse:
    return _attendance_detail(_get_owned_attendance(db, user, attendance_id))


def update_attendance(db: Session, user: User, attendance_id: str, payload: SchoolAttendanceUpdateRequest) -> SchoolAttendanceDetailResponse:
    attendance = _get_owned_attendance(db, user, attendance_id)
    data = payload.model_dump(exclude_unset=True)
    attendance_date = data.get("attendance_date", attendance.attendance_date)
    _assert_attendance_unique(db, user, attendance.class_id, attendance.student_id, attendance_date, attendance.id)
    for field, value in data.items():
        setattr(attendance, field, value)
    db.commit()
    db.refresh(attendance)
    return _attendance_detail(attendance)


def delete_attendance(db: Session, user: User, attendance_id: str) -> None:
    attendance = _get_owned_attendance(db, user, attendance_id)
    repository.delete_record(db, attendance)
    db.commit()


def get_dashboard(db: Session, user: User) -> SchoolDashboardResponse:
    raw_students = repository.list_students(db, user.id)
    raw_classes = repository.list_classes(db, user.id)
    raw_attendance = repository.list_attendance(db, user.id)
    students = [_student_summary(student) for student in raw_students]
    classes = [_class_summary(school_class) for school_class in raw_classes]
    attendance = [_attendance_summary(record) for record in raw_attendance]
    now = datetime.now(UTC)
    new_admissions = sum(1 for student in raw_students if student.admission_date and student.admission_date[:7] == now.strftime("%Y-%m"))
    active_enrollments = [enrollment for school_class in raw_classes for enrollment in _active_enrollments(school_class.enrollments)]
    students_by_class = [SchoolBreakdownResponse(label=school_class.class_name, count=len(_active_enrollments(school_class.enrollments))) for school_class in raw_classes]
    students_by_status = [SchoolBreakdownResponse(label=label, count=count) for label, count in sorted(Counter(student.status for student in raw_students).items())]
    attendance_by_class_counter = Counter(record.school_class.class_name if record.school_class else "Class" for record in raw_attendance)
    attendance_by_class = [SchoolBreakdownResponse(label=label, count=count) for label, count in sorted(attendance_by_class_counter.items())]
    monthly_counter: dict[str, int] = defaultdict(int)
    for record in raw_attendance:
        monthly_counter[record.attendance_date[:7]] += 1
    monthly_attendance_activity = [SchoolBreakdownResponse(label=label, count=count) for label, count in sorted(monthly_counter.items())[-6:]]
    return SchoolDashboardResponse(
        students=students,
        classes=classes,
        attendance=attendance,
        total_students=len(raw_students),
        active_students=sum(1 for student in raw_students if student.status == "active"),
        new_admissions=new_admissions,
        inactive_students=sum(1 for student in raw_students if student.status == "inactive"),
        total_classes=len(raw_classes),
        active_classes=sum(1 for school_class in raw_classes if school_class.status == "active"),
        total_enrollments=len(active_enrollments),
        available_seats=sum(max((school_class.capacity or 0) - len(_active_enrollments(school_class.enrollments)), 0) for school_class in raw_classes),
        present_count=sum(1 for record in raw_attendance if record.status == "present"),
        absent_count=sum(1 for record in raw_attendance if record.status == "absent"),
        late_count=sum(1 for record in raw_attendance if record.status == "late"),
        attendance_rate=_attendance_rate(raw_attendance),
        students_by_class=students_by_class,
        students_by_status=students_by_status,
        attendance_by_class=attendance_by_class,
        monthly_attendance_activity=monthly_attendance_activity,
        recent_admissions=sorted(students, key=lambda item: item.admission_date or "", reverse=True)[:5],
        recent_activity=attendance[:8],
    )
