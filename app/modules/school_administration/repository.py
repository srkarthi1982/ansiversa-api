from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.school_administration.models import SchoolAttendance, SchoolClass, SchoolEnrollment, SchoolStudent


def get_student(db: Session, student_id: str) -> SchoolStudent | None:
    return db.get(SchoolStudent, student_id)


def get_class(db: Session, class_id: str) -> SchoolClass | None:
    return db.get(SchoolClass, class_id)


def get_enrollment(db: Session, enrollment_id: str) -> SchoolEnrollment | None:
    return db.get(SchoolEnrollment, enrollment_id)


def get_attendance(db: Session, attendance_id: str) -> SchoolAttendance | None:
    return db.get(SchoolAttendance, attendance_id)


def list_students(db: Session, owner_id: str) -> list[SchoolStudent]:
    return list(
        db.execute(
            select(SchoolStudent)
            .options(joinedload(SchoolStudent.enrollments).joinedload(SchoolEnrollment.school_class))
            .where(SchoolStudent.owner_id == owner_id)
            .order_by(SchoolStudent.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_classes(db: Session, owner_id: str) -> list[SchoolClass]:
    return list(
        db.execute(
            select(SchoolClass)
            .options(joinedload(SchoolClass.enrollments).joinedload(SchoolEnrollment.student))
            .where(SchoolClass.owner_id == owner_id)
            .order_by(SchoolClass.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_attendance(db: Session, owner_id: str) -> list[SchoolAttendance]:
    return list(
        db.execute(
            select(SchoolAttendance)
            .options(joinedload(SchoolAttendance.school_class), joinedload(SchoolAttendance.student))
            .where(SchoolAttendance.owner_id == owner_id)
            .order_by(SchoolAttendance.attendance_date.desc(), SchoolAttendance.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def find_student_by_admission_number(db: Session, owner_id: str, admission_number: str) -> SchoolStudent | None:
    return db.execute(
        select(SchoolStudent).where(
            SchoolStudent.owner_id == owner_id,
            SchoolStudent.admission_number == admission_number,
        )
    ).scalar_one_or_none()


def find_active_enrollment(db: Session, owner_id: str, class_id: str, student_id: str) -> SchoolEnrollment | None:
    return db.execute(
        select(SchoolEnrollment).where(
            SchoolEnrollment.owner_id == owner_id,
            SchoolEnrollment.class_id == class_id,
            SchoolEnrollment.student_id == student_id,
            SchoolEnrollment.status == "active",
        )
    ).scalar_one_or_none()


def find_attendance(db: Session, owner_id: str, class_id: str, student_id: str, attendance_date: str) -> SchoolAttendance | None:
    return db.execute(
        select(SchoolAttendance).where(
            SchoolAttendance.owner_id == owner_id,
            SchoolAttendance.class_id == class_id,
            SchoolAttendance.student_id == student_id,
            SchoolAttendance.attendance_date == attendance_date,
        )
    ).scalar_one_or_none()


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
