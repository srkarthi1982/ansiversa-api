from fastapi import APIRouter, Response, status

from app.modules.school_administration import service
from app.modules.school_administration.dependencies import CurrentSchoolAdministrationUser, SchoolAdministrationDB
from app.modules.school_administration.schemas import (
    SchoolAttendanceCreateRequest,
    SchoolAttendanceDetailResponse,
    SchoolAttendanceSummaryResponse,
    SchoolAttendanceUpdateRequest,
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

router = APIRouter()


@router.get("/dashboard", response_model=SchoolDashboardResponse, operation_id="getSchoolAdministrationDashboard")
def get_dashboard(db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.get_dashboard(db, current_user)


@router.get("/students", response_model=list[SchoolStudentSummaryResponse], operation_id="listSchoolStudents")
def list_students(db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.list_students(db, current_user)


@router.post("/students", response_model=SchoolStudentDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSchoolStudent")
def create_student(payload: SchoolStudentCreateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.create_student(db, current_user, payload)


@router.get("/students/{student_id}", response_model=SchoolStudentDetailResponse, operation_id="getSchoolStudent")
def get_student(student_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.get_student(db, current_user, student_id)


@router.put("/students/{student_id}", response_model=SchoolStudentDetailResponse, operation_id="updateSchoolStudent")
def update_student(student_id: str, payload: SchoolStudentUpdateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.update_student(db, current_user, student_id, payload)


@router.post("/students/{student_id}/duplicate", response_model=SchoolStudentDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateSchoolStudent")
def duplicate_student(student_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.duplicate_student(db, current_user, student_id)


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSchoolStudent")
def delete_student(student_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    service.delete_student(db, current_user, student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/classes", response_model=list[SchoolClassSummaryResponse], operation_id="listSchoolClasses")
def list_classes(db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.list_classes(db, current_user)


@router.post("/classes", response_model=SchoolClassDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSchoolClass")
def create_class(payload: SchoolClassCreateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.create_class(db, current_user, payload)


@router.get("/classes/{class_id}", response_model=SchoolClassDetailResponse, operation_id="getSchoolClass")
def get_class(class_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.get_class(db, current_user, class_id)


@router.put("/classes/{class_id}", response_model=SchoolClassDetailResponse, operation_id="updateSchoolClass")
def update_class(class_id: str, payload: SchoolClassUpdateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.update_class(db, current_user, class_id, payload)


@router.post("/classes/{class_id}/duplicate", response_model=SchoolClassDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateSchoolClass")
def duplicate_class(class_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.duplicate_class(db, current_user, class_id)


@router.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSchoolClass")
def delete_class(class_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    service.delete_class(db, current_user, class_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/enrollments", response_model=SchoolEnrollmentResponse, status_code=status.HTTP_201_CREATED, operation_id="createSchoolEnrollment")
def create_enrollment(payload: SchoolEnrollmentCreateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.create_enrollment(db, current_user, payload)


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSchoolEnrollment")
def delete_enrollment(enrollment_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    service.delete_enrollment(db, current_user, enrollment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/attendance", response_model=list[SchoolAttendanceSummaryResponse], operation_id="listSchoolAttendance")
def list_attendance(db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.list_attendance(db, current_user)


@router.post("/attendance", response_model=SchoolAttendanceDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSchoolAttendance")
def create_attendance(payload: SchoolAttendanceCreateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.create_attendance(db, current_user, payload)


@router.get("/attendance/{attendance_id}", response_model=SchoolAttendanceDetailResponse, operation_id="getSchoolAttendance")
def get_attendance(attendance_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.get_attendance(db, current_user, attendance_id)


@router.put("/attendance/{attendance_id}", response_model=SchoolAttendanceDetailResponse, operation_id="updateSchoolAttendance")
def update_attendance(attendance_id: str, payload: SchoolAttendanceUpdateRequest, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    return service.update_attendance(db, current_user, attendance_id, payload)


@router.delete("/attendance/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSchoolAttendance")
def delete_attendance(attendance_id: str, db: SchoolAdministrationDB, current_user: CurrentSchoolAdministrationUser):
    service.delete_attendance(db, current_user, attendance_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
