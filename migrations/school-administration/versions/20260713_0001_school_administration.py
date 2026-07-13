"""add school administration tables

Revision ID: 20260713_0001_school_administration
Revises:
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260713_0001_school_administration"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEXES = (
    ("SchoolStudents_userId_status_updatedAt_idx", "SchoolStudents", ("userId", "status", "updatedAt")),
    ("SchoolStudents_userId_createdAt_idx", "SchoolStudents", ("userId", "createdAt")),
    ("SchoolClasses_userId_year_status_idx", "SchoolClasses", ("userId", "academicYear", "status")),
    ("SchoolClasses_userId_updatedAt_idx", "SchoolClasses", ("userId", "updatedAt")),
    ("SchoolEnrollments_userId_classId_status_idx", "SchoolEnrollments", ("userId", "classId", "status")),
    ("SchoolEnrollments_userId_studentId_status_idx", "SchoolEnrollments", ("userId", "studentId", "status")),
    ("SchoolAttendance_userId_classId_date_status_idx", "SchoolAttendance", ("userId", "classId", "attendanceDate", "status")),
    ("SchoolAttendance_userId_studentId_date_idx", "SchoolAttendance", ("userId", "studentId", "attendanceDate")),
    ("SchoolAttendance_userId_date_idx", "SchoolAttendance", ("userId", "attendanceDate")),
)


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _create_index_if_missing(name: str, table_name: str, columns: Sequence[str]) -> None:
    if name not in _index_names(table_name):
        op.create_index(name, table_name, list(columns))


def upgrade() -> None:
    table_names = _table_names()

    if "SchoolStudents" not in table_names:
        op.create_table(
            "SchoolStudents",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("admissionNumber", sa.String(length=80), nullable=False),
            sa.Column("fullName", sa.String(length=180), nullable=False),
            sa.Column("dateOfBirth", sa.String(length=40), nullable=True),
            sa.Column("gender", sa.String(length=40), nullable=True),
            sa.Column("guardianName", sa.String(length=180), nullable=True),
            sa.Column("guardianPhone", sa.String(length=80), nullable=True),
            sa.Column("guardianEmail", sa.String(length=180), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("admissionDate", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("emergencyContact", sa.String(length=180), nullable=True),
            sa.Column("supportNote", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "admissionNumber", name="SchoolStudents_userId_admissionNumber_key"),
        )
        op.create_index("ix_SchoolStudents_userId", "SchoolStudents", ["userId"])

    if "SchoolClasses" not in table_names:
        op.create_table(
            "SchoolClasses",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("className", sa.String(length=160), nullable=False),
            sa.Column("gradeLevel", sa.String(length=80), nullable=True),
            sa.Column("section", sa.String(length=80), nullable=True),
            sa.Column("academicYear", sa.String(length=40), nullable=False),
            sa.Column("classTeacher", sa.String(length=180), nullable=True),
            sa.Column("room", sa.String(length=80), nullable=True),
            sa.Column("capacity", sa.Integer(), server_default="0", nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("scheduleNote", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_SchoolClasses_userId", "SchoolClasses", ["userId"])

    if "SchoolEnrollments" not in table_names:
        op.create_table(
            "SchoolEnrollments",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("classId", sa.String(length=36), nullable=False),
            sa.Column("studentId", sa.String(length=36), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="active", nullable=False),
            sa.Column("enrolledAt", sa.String(length=40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["classId"], ["SchoolClasses.id"]),
            sa.ForeignKeyConstraint(["studentId"], ["SchoolStudents.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "classId", "studentId", "status", name="SchoolEnrollments_userId_classId_studentId_status_key"),
        )
        op.create_index("ix_SchoolEnrollments_userId", "SchoolEnrollments", ["userId"])
        op.create_index("ix_SchoolEnrollments_classId", "SchoolEnrollments", ["classId"])
        op.create_index("ix_SchoolEnrollments_studentId", "SchoolEnrollments", ["studentId"])

    if "SchoolAttendance" not in table_names:
        op.create_table(
            "SchoolAttendance",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("userId", sa.String(length=36), nullable=False),
            sa.Column("classId", sa.String(length=36), nullable=False),
            sa.Column("studentId", sa.String(length=36), nullable=False),
            sa.Column("attendanceDate", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=40), server_default="present", nullable=False),
            sa.Column("arrivalTime", sa.String(length=40), nullable=True),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("recordedBy", sa.String(length=180), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("createdAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["classId"], ["SchoolClasses.id"]),
            sa.ForeignKeyConstraint(["studentId"], ["SchoolStudents.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("userId", "classId", "studentId", "attendanceDate", name="SchoolAttendance_userId_classId_studentId_date_key"),
        )
        op.create_index("ix_SchoolAttendance_userId", "SchoolAttendance", ["userId"])
        op.create_index("ix_SchoolAttendance_classId", "SchoolAttendance", ["classId"])
        op.create_index("ix_SchoolAttendance_studentId", "SchoolAttendance", ["studentId"])

    for name, table_name, columns in INDEXES:
        _create_index_if_missing(name, table_name, columns)


def downgrade() -> None:
    table_names = _table_names()
    if "SchoolAttendance" in table_names:
        op.drop_table("SchoolAttendance")
    if "SchoolEnrollments" in table_names:
        op.drop_table("SchoolEnrollments")
    if "SchoolClasses" in table_names:
        op.drop_table("SchoolClasses")
    if "SchoolStudents" in table_names:
        op.drop_table("SchoolStudents")
