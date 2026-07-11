from fastapi import APIRouter, Response, status

from app.modules.medicine_reminder import service
from app.modules.medicine_reminder.dependencies import CurrentMedicineReminderUser, MedicineReminderDB
from app.modules.medicine_reminder.schemas import (
    DoseLogCreateRequest,
    DoseLogDetailResponse,
    DoseLogSummaryResponse,
    DoseLogUpdateRequest,
    MedicineCreateRequest,
    MedicineDetailResponse,
    MedicineReminderDashboardResponse,
    MedicineSummaryResponse,
    MedicineUpdateRequest,
    MedicineReminderNoteCreateRequest,
    MedicineReminderNoteDetailResponse,
    MedicineReminderNoteSummaryResponse,
    MedicineReminderNoteUpdateRequest,
    ScheduleCreateRequest,
    ScheduleDetailResponse,
    ScheduleSummaryResponse,
    ScheduleUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=MedicineReminderDashboardResponse)
def get_dashboard(db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.get_dashboard(db, current_user)


@router.get("/medicines", response_model=list[MedicineSummaryResponse])
def list_medicines(db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.list_medicines(db, current_user)


@router.post("/medicines", response_model=MedicineDetailResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(payload: MedicineCreateRequest, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.create_medicine(db, current_user, payload)


@router.get("/medicines/{medicine_id}", response_model=MedicineDetailResponse)
def get_medicine(medicine_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.get_medicine(db, current_user, medicine_id)


@router.put("/medicines/{medicine_id}", response_model=MedicineDetailResponse)
def update_medicine(
    medicine_id: str,
    payload: MedicineUpdateRequest,
    db: MedicineReminderDB,
    current_user: CurrentMedicineReminderUser,
):
    return service.update_medicine(db, current_user, medicine_id, payload)


@router.delete("/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(medicine_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    service.delete_medicine(db, current_user, medicine_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/schedules", response_model=list[ScheduleSummaryResponse])
def list_schedules(db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.list_schedules(db, current_user)


@router.post("/schedules", response_model=ScheduleDetailResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(payload: ScheduleCreateRequest, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.create_schedule(db, current_user, payload)


@router.get("/schedules/{schedule_id}", response_model=ScheduleDetailResponse)
def get_schedule(schedule_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.get_schedule(db, current_user, schedule_id)


@router.put("/schedules/{schedule_id}", response_model=ScheduleDetailResponse)
def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdateRequest,
    db: MedicineReminderDB,
    current_user: CurrentMedicineReminderUser,
):
    return service.update_schedule(db, current_user, schedule_id, payload)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    service.delete_schedule(db, current_user, schedule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dose-logs", response_model=list[DoseLogSummaryResponse])
def list_dose_logs(db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.list_dose_logs(db, current_user)


@router.post("/dose-logs", response_model=DoseLogDetailResponse, status_code=status.HTTP_201_CREATED)
def create_dose_log(payload: DoseLogCreateRequest, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.create_dose_log(db, current_user, payload)


@router.get("/dose-logs/{dose_log_id}", response_model=DoseLogDetailResponse)
def get_dose_log(dose_log_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.get_dose_log(db, current_user, dose_log_id)


@router.put("/dose-logs/{dose_log_id}", response_model=DoseLogDetailResponse)
def update_dose_log(
    dose_log_id: str,
    payload: DoseLogUpdateRequest,
    db: MedicineReminderDB,
    current_user: CurrentMedicineReminderUser,
):
    return service.update_dose_log(db, current_user, dose_log_id, payload)


@router.delete("/dose-logs/{dose_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dose_log(dose_log_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    service.delete_dose_log(db, current_user, dose_log_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notes", response_model=list[MedicineReminderNoteSummaryResponse])
def list_notes(db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.list_notes(db, current_user)


@router.post("/notes", response_model=MedicineReminderNoteDetailResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: MedicineReminderNoteCreateRequest, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.create_note(db, current_user, payload)


@router.get("/notes/{note_id}", response_model=MedicineReminderNoteDetailResponse)
def get_note(note_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    return service.get_note(db, current_user, note_id)


@router.put("/notes/{note_id}", response_model=MedicineReminderNoteDetailResponse)
def update_note(
    note_id: str,
    payload: MedicineReminderNoteUpdateRequest,
    db: MedicineReminderDB,
    current_user: CurrentMedicineReminderUser,
):
    return service.update_note(db, current_user, note_id, payload)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, db: MedicineReminderDB, current_user: CurrentMedicineReminderUser):
    service.delete_note(db, current_user, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
