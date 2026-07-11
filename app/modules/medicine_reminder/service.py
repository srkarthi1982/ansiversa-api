from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.medicine_reminder import repository
from app.modules.medicine_reminder.models import (
    MedicineReminderDoseLog,
    MedicineReminderMedicine,
    MedicineReminderNote,
    MedicineReminderSchedule,
)
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

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_medicine(db: Session, user: User, medicine_id: str) -> MedicineReminderMedicine:
    medicine = repository.get_medicine(db, medicine_id)
    if not medicine or medicine.owner_id != user.id:
        _not_found("Medicine was not found.")
    return medicine


def _get_owned_schedule(db: Session, user: User, schedule_id: str) -> MedicineReminderSchedule:
    schedule = repository.get_schedule(db, schedule_id)
    if not schedule or schedule.owner_id != user.id:
        _not_found("Schedule was not found.")
    return schedule


def _get_owned_dose_log(db: Session, user: User, dose_log_id: str) -> MedicineReminderDoseLog:
    dose_log = repository.get_dose_log(db, dose_log_id)
    if not dose_log or dose_log.owner_id != user.id:
        _not_found("Dose log was not found.")
    return dose_log


def _get_owned_note(db: Session, user: User, note_id: str) -> MedicineReminderNote:
    note = repository.get_note(db, note_id)
    if not note or note.owner_id != user.id:
        _not_found("Note was not found.")
    return note


def _medicine_summary_response(medicine: MedicineReminderMedicine) -> MedicineSummaryResponse:
    dose_logs = sorted(medicine.dose_logs, key=lambda item: (item.scheduled_for, item.created_at), reverse=True)
    taken_logs = [dose_log for dose_log in dose_logs if dose_log.status in {"taken", "late"}]
    return MedicineSummaryResponse(
        id=medicine.id,
        name=medicine.name,
        dosage=medicine.dosage,
        form=medicine.form,
        purpose=medicine.purpose,
        instructions_preview=_preview(medicine.instructions),
        prescribing_doctor=medicine.prescribing_doctor,
        start_date=medicine.start_date,
        end_date=medicine.end_date,
        status=medicine.status,
        refill_quantity=medicine.refill_quantity,
        refill_reminder_date=medicine.refill_reminder_date,
        schedule_count=len(medicine.schedules),
        active_schedule_count=sum(1 for schedule in medicine.schedules if schedule.status == "active"),
        dose_log_count=len(medicine.dose_logs),
        last_taken_at=taken_logs[0].taken_at or taken_logs[0].scheduled_for if taken_logs else None,
        created_at=medicine.created_at,
        updated_at=medicine.updated_at,
    )


def _schedule_summary_response(schedule: MedicineReminderSchedule) -> ScheduleSummaryResponse:
    return ScheduleSummaryResponse(
        id=schedule.id,
        medicine_id=schedule.medicine_id,
        medicine_name=schedule.medicine.name,
        label=schedule.label,
        time_of_day=schedule.time_of_day,
        frequency=schedule.frequency,
        days_of_week=schedule.days_of_week,
        dose_amount=schedule.dose_amount,
        instructions_preview=_preview(schedule.instructions),
        status=schedule.status,
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def _dose_log_summary_response(dose_log: MedicineReminderDoseLog) -> DoseLogSummaryResponse:
    return DoseLogSummaryResponse(
        id=dose_log.id,
        medicine_id=dose_log.medicine_id,
        medicine_name=dose_log.medicine.name,
        schedule_id=dose_log.schedule_id,
        schedule_label=dose_log.schedule.label if dose_log.schedule else None,
        scheduled_for=dose_log.scheduled_for,
        taken_at=dose_log.taken_at,
        status=dose_log.status,
        note_preview=_preview(dose_log.note),
        created_at=dose_log.created_at,
        updated_at=dose_log.updated_at,
    )


def _note_summary_response(note: MedicineReminderNote) -> MedicineReminderNoteSummaryResponse:
    return MedicineReminderNoteSummaryResponse(
        id=note.id,
        medicine_id=note.medicine_id,
        medicine_name=note.medicine.name,
        note_date=note.note_date,
        title=note.title,
        body_preview=_preview(note.body),
        category=note.category,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _medicine_detail_response(medicine: MedicineReminderMedicine) -> MedicineDetailResponse:
    summary = _medicine_summary_response(medicine)
    schedules = sorted(medicine.schedules, key=lambda item: (item.time_of_day, item.updated_at))
    dose_logs = sorted(medicine.dose_logs, key=lambda item: (item.scheduled_for, item.created_at), reverse=True)
    notes = sorted(medicine.notes, key=lambda item: (item.note_date, item.updated_at), reverse=True)
    return MedicineDetailResponse(
        **summary.model_dump(),
        instructions=medicine.instructions,
        schedules=[_schedule_summary_response(schedule) for schedule in schedules],
        dose_logs=[_dose_log_summary_response(dose_log) for dose_log in dose_logs],
        notes=[_note_summary_response(note) for note in notes],
    )


def _schedule_detail_response(schedule: MedicineReminderSchedule) -> ScheduleDetailResponse:
    return ScheduleDetailResponse(**_schedule_summary_response(schedule).model_dump(), instructions=schedule.instructions)


def _dose_log_detail_response(dose_log: MedicineReminderDoseLog) -> DoseLogDetailResponse:
    return DoseLogDetailResponse(**_dose_log_summary_response(dose_log).model_dump(), note=dose_log.note)


def _note_detail_response(note: MedicineReminderNote) -> MedicineReminderNoteDetailResponse:
    return MedicineReminderNoteDetailResponse(**_note_summary_response(note).model_dump(), body=note.body)


def list_medicines(db: Session, user: User) -> list[MedicineSummaryResponse]:
    return [_medicine_summary_response(medicine) for medicine in repository.list_medicines(db, user.id)]


def create_medicine(db: Session, user: User, payload: MedicineCreateRequest) -> MedicineDetailResponse:
    medicine = MedicineReminderMedicine(owner_id=user.id, **payload.model_dump())
    repository.add(db, medicine)
    db.commit()
    db.refresh(medicine)
    return _medicine_detail_response(medicine)


def get_medicine(db: Session, user: User, medicine_id: str) -> MedicineDetailResponse:
    return _medicine_detail_response(_get_owned_medicine(db, user, medicine_id))


def update_medicine(db: Session, user: User, medicine_id: str, payload: MedicineUpdateRequest) -> MedicineDetailResponse:
    medicine = _get_owned_medicine(db, user, medicine_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(medicine, field, value)
    db.commit()
    db.refresh(medicine)
    return _medicine_detail_response(medicine)


def delete_medicine(db: Session, user: User, medicine_id: str) -> None:
    medicine = _get_owned_medicine(db, user, medicine_id)
    repository.delete_record(db, medicine)
    db.commit()


def list_schedules(db: Session, user: User) -> list[ScheduleSummaryResponse]:
    return [_schedule_summary_response(schedule) for schedule in repository.list_schedules(db, user.id)]


def create_schedule(db: Session, user: User, payload: ScheduleCreateRequest) -> ScheduleDetailResponse:
    data = payload.model_dump()
    _get_owned_medicine(db, user, data["medicine_id"])
    schedule = MedicineReminderSchedule(owner_id=user.id, **data)
    repository.add(db, schedule)
    db.commit()
    db.refresh(schedule)
    return _schedule_detail_response(schedule)


def get_schedule(db: Session, user: User, schedule_id: str) -> ScheduleDetailResponse:
    return _schedule_detail_response(_get_owned_schedule(db, user, schedule_id))


def update_schedule(db: Session, user: User, schedule_id: str, payload: ScheduleUpdateRequest) -> ScheduleDetailResponse:
    schedule = _get_owned_schedule(db, user, schedule_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return _schedule_detail_response(schedule)


def delete_schedule(db: Session, user: User, schedule_id: str) -> None:
    schedule = _get_owned_schedule(db, user, schedule_id)
    repository.delete_record(db, schedule)
    db.commit()


def list_dose_logs(db: Session, user: User) -> list[DoseLogSummaryResponse]:
    return [_dose_log_summary_response(dose_log) for dose_log in repository.list_dose_logs(db, user.id)]


def create_dose_log(db: Session, user: User, payload: DoseLogCreateRequest) -> DoseLogDetailResponse:
    data = payload.model_dump()
    _get_owned_medicine(db, user, data["medicine_id"])
    if data.get("schedule_id"):
        schedule = _get_owned_schedule(db, user, data["schedule_id"])
        if schedule.medicine_id != data["medicine_id"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Schedule does not belong to this medicine.")
    dose_log = MedicineReminderDoseLog(owner_id=user.id, **data)
    repository.add(db, dose_log)
    db.commit()
    db.refresh(dose_log)
    return _dose_log_detail_response(dose_log)


def get_dose_log(db: Session, user: User, dose_log_id: str) -> DoseLogDetailResponse:
    return _dose_log_detail_response(_get_owned_dose_log(db, user, dose_log_id))


def update_dose_log(db: Session, user: User, dose_log_id: str, payload: DoseLogUpdateRequest) -> DoseLogDetailResponse:
    dose_log = _get_owned_dose_log(db, user, dose_log_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dose_log, field, value)
    db.commit()
    db.refresh(dose_log)
    return _dose_log_detail_response(dose_log)


def delete_dose_log(db: Session, user: User, dose_log_id: str) -> None:
    dose_log = _get_owned_dose_log(db, user, dose_log_id)
    repository.delete_record(db, dose_log)
    db.commit()


def list_notes(db: Session, user: User) -> list[MedicineReminderNoteSummaryResponse]:
    return [_note_summary_response(note) for note in repository.list_notes(db, user.id)]


def create_note(db: Session, user: User, payload: MedicineReminderNoteCreateRequest) -> MedicineReminderNoteDetailResponse:
    data = payload.model_dump()
    _get_owned_medicine(db, user, data["medicine_id"])
    note = MedicineReminderNote(owner_id=user.id, **data)
    repository.add(db, note)
    db.commit()
    db.refresh(note)
    return _note_detail_response(note)


def get_note(db: Session, user: User, note_id: str) -> MedicineReminderNoteDetailResponse:
    return _note_detail_response(_get_owned_note(db, user, note_id))


def update_note(db: Session, user: User, note_id: str, payload: MedicineReminderNoteUpdateRequest) -> MedicineReminderNoteDetailResponse:
    note = _get_owned_note(db, user, note_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return _note_detail_response(note)


def delete_note(db: Session, user: User, note_id: str) -> None:
    note = _get_owned_note(db, user, note_id)
    repository.delete_record(db, note)
    db.commit()


def get_dashboard(db: Session, user: User) -> MedicineReminderDashboardResponse:
    medicines = repository.list_medicines(db, user.id)
    schedules = repository.list_schedules(db, user.id)
    dose_logs = repository.list_dose_logs(db, user.id)
    notes = repository.list_notes(db, user.id)
    week_start = (date.today() - timedelta(days=6)).isoformat()
    today = date.today().isoformat()
    return MedicineReminderDashboardResponse(
        medicines=[_medicine_summary_response(medicine) for medicine in medicines],
        schedules=[_schedule_summary_response(schedule) for schedule in schedules],
        dose_logs=[_dose_log_summary_response(dose_log) for dose_log in dose_logs],
        notes=[_note_summary_response(note) for note in notes],
        active_medicine_count=sum(1 for medicine in medicines if medicine.status == "active"),
        active_schedule_count=sum(1 for schedule in schedules if schedule.status == "active"),
        doses_logged_this_week=sum(1 for dose_log in dose_logs if dose_log.scheduled_for[:10] >= week_start),
        missed_dose_count=sum(1 for dose_log in dose_logs if dose_log.status == "missed"),
        refill_watch_count=sum(
            1
            for medicine in medicines
            if medicine.status == "active" and medicine.refill_reminder_date and medicine.refill_reminder_date <= today
        ),
        recent_dose_logs=[_dose_log_summary_response(dose_log) for dose_log in dose_logs[:6]],
    )
