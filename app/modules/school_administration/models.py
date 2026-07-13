from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.school_administration.db import SchoolAdministrationBase


def _uuid() -> str:
    return str(uuid4())


class SchoolStudent(SchoolAdministrationBase):
    __tablename__ = "SchoolStudents"
    __table_args__ = (
        UniqueConstraint("userId", "admissionNumber", name="SchoolStudents_userId_admissionNumber_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    admission_number: Mapped[str] = mapped_column("admissionNumber", String(80), nullable=False)
    full_name: Mapped[str] = mapped_column("fullName", String(180), nullable=False)
    date_of_birth: Mapped[str | None] = mapped_column("dateOfBirth", String(40), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(40), nullable=True)
    guardian_name: Mapped[str | None] = mapped_column("guardianName", String(180), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column("guardianPhone", String(80), nullable=True)
    guardian_email: Mapped[str | None] = mapped_column("guardianEmail", String(180), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    admission_date: Mapped[str | None] = mapped_column("admissionDate", String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    emergency_contact: Mapped[str | None] = mapped_column("emergencyContact", String(180), nullable=True)
    support_note: Mapped[str | None] = mapped_column("supportNote", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    enrollments: Mapped[list["SchoolEnrollment"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    attendance_records: Mapped[list["SchoolAttendance"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class SchoolClass(SchoolAdministrationBase):
    __tablename__ = "SchoolClasses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    class_name: Mapped[str] = mapped_column("className", String(160), nullable=False)
    grade_level: Mapped[str | None] = mapped_column("gradeLevel", String(80), nullable=True)
    section: Mapped[str | None] = mapped_column(String(80), nullable=True)
    academic_year: Mapped[str] = mapped_column("academicYear", String(40), nullable=False)
    class_teacher: Mapped[str | None] = mapped_column("classTeacher", String(180), nullable=True)
    room: Mapped[str | None] = mapped_column(String(80), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    schedule_note: Mapped[str | None] = mapped_column("scheduleNote", Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    enrollments: Mapped[list["SchoolEnrollment"]] = relationship(back_populates="school_class", cascade="all, delete-orphan")
    attendance_records: Mapped[list["SchoolAttendance"]] = relationship(back_populates="school_class", cascade="all, delete-orphan")


class SchoolEnrollment(SchoolAdministrationBase):
    __tablename__ = "SchoolEnrollments"
    __table_args__ = (
        UniqueConstraint("userId", "classId", "studentId", "status", name="SchoolEnrollments_userId_classId_studentId_status_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    class_id: Mapped[str] = mapped_column("classId", String(36), ForeignKey("SchoolClasses.id"), index=True, nullable=False)
    student_id: Mapped[str] = mapped_column("studentId", String(36), ForeignKey("SchoolStudents.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", server_default="active", nullable=False)
    enrolled_at: Mapped[str | None] = mapped_column("enrolledAt", String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    school_class: Mapped[SchoolClass] = relationship(back_populates="enrollments")
    student: Mapped[SchoolStudent] = relationship(back_populates="enrollments")


class SchoolAttendance(SchoolAdministrationBase):
    __tablename__ = "SchoolAttendance"
    __table_args__ = (
        UniqueConstraint("userId", "classId", "studentId", "attendanceDate", name="SchoolAttendance_userId_classId_studentId_date_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    class_id: Mapped[str] = mapped_column("classId", String(36), ForeignKey("SchoolClasses.id"), index=True, nullable=False)
    student_id: Mapped[str] = mapped_column("studentId", String(36), ForeignKey("SchoolStudents.id"), index=True, nullable=False)
    attendance_date: Mapped[str] = mapped_column("attendanceDate", String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="present", server_default="present", nullable=False)
    arrival_time: Mapped[str | None] = mapped_column("arrivalTime", String(40), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[str | None] = mapped_column("recordedBy", String(180), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    school_class: Mapped[SchoolClass] = relationship(back_populates="attendance_records")
    student: Mapped[SchoolStudent] = relationship(back_populates="attendance_records")
