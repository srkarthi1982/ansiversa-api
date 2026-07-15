from fastapi import APIRouter, Query, Response, status

from app.modules.birthday_and_anniversary_reminder import service
from app.modules.birthday_and_anniversary_reminder.dependencies import BirthdayReminderDB, CurrentBirthdayReminderUser
from app.modules.birthday_and_anniversary_reminder.schemas import (
    ArchiveFilter,
    DashboardResponse,
    FavouriteFilter,
    InsightsResponse,
    ReminderCreateRequest,
    ReminderDetailResponse,
    ReminderSort,
    ReminderSummaryResponse,
    ReminderTypeCreateRequest,
    ReminderTypeResponse,
    ReminderTypeUpdateRequest,
    ReminderUpdateRequest,
    TimeFilter,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getBirthdayAnniversaryReminderDashboard")
def get_dashboard(db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getBirthdayAnniversaryReminderInsights")
def get_insights(db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.get_insights(db, current_user)


@router.get("/types", response_model=list[ReminderTypeResponse], operation_id="listBirthdayAnniversaryReminderTypes")
def list_types(db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.list_types(db, current_user)


@router.post("/types", response_model=ReminderTypeResponse, status_code=status.HTTP_201_CREATED, operation_id="createBirthdayAnniversaryReminderType")
def create_type(payload: ReminderTypeCreateRequest, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.create_type(db, current_user, payload)


@router.put("/types/{type_id}", response_model=ReminderTypeResponse, operation_id="updateBirthdayAnniversaryReminderType")
def update_type(type_id: str, payload: ReminderTypeUpdateRequest, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.update_type(db, current_user, type_id, payload)


@router.delete("/types/{type_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteBirthdayAnniversaryReminderType")
def delete_type(type_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    service.delete_type(db, current_user, type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reminders", response_model=list[ReminderSummaryResponse], operation_id="listBirthdayAnniversaryReminders")
def list_reminders(
    db: BirthdayReminderDB,
    current_user: CurrentBirthdayReminderUser,
    q: str | None = Query(default=None),
    archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"),
    favourite_filter: FavouriteFilter = Query(default="all", alias="favouriteFilter"),
    type_id: str | None = Query(default=None, alias="typeId"),
    time_filter: TimeFilter = Query(default="all", alias="timeFilter"),
    sort_by: ReminderSort = Query(default="upcoming", alias="sortBy"),
):
    return service.list_reminders(db, current_user, q, archive_filter, favourite_filter, type_id, time_filter, sort_by)


@router.post("/reminders", response_model=ReminderDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createBirthdayAnniversaryReminder")
def create_reminder(payload: ReminderCreateRequest, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.create_reminder(db, current_user, payload)


@router.get("/reminders/{reminder_id}", response_model=ReminderDetailResponse, operation_id="getBirthdayAnniversaryReminder")
def get_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.get_reminder(db, current_user, reminder_id)


@router.put("/reminders/{reminder_id}", response_model=ReminderDetailResponse, operation_id="updateBirthdayAnniversaryReminder")
def update_reminder(reminder_id: str, payload: ReminderUpdateRequest, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.update_reminder(db, current_user, reminder_id, payload)


@router.post("/reminders/{reminder_id}/archive", response_model=ReminderDetailResponse, operation_id="archiveBirthdayAnniversaryReminder")
def archive_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.set_reminder_archived(db, current_user, reminder_id, True)


@router.post("/reminders/{reminder_id}/restore", response_model=ReminderDetailResponse, operation_id="restoreBirthdayAnniversaryReminder")
def restore_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.set_reminder_archived(db, current_user, reminder_id, False)


@router.post("/reminders/{reminder_id}/favourite", response_model=ReminderDetailResponse, operation_id="favouriteBirthdayAnniversaryReminder")
def favourite_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.set_reminder_favourite(db, current_user, reminder_id, True)


@router.post("/reminders/{reminder_id}/unfavourite", response_model=ReminderDetailResponse, operation_id="unfavouriteBirthdayAnniversaryReminder")
def unfavourite_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.set_reminder_favourite(db, current_user, reminder_id, False)


@router.post("/reminders/{reminder_id}/acknowledge", response_model=ReminderDetailResponse, operation_id="acknowledgeBirthdayAnniversaryReminder")
def acknowledge_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    return service.acknowledge_reminder(db, current_user, reminder_id)


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteBirthdayAnniversaryReminder")
def delete_reminder(reminder_id: str, db: BirthdayReminderDB, current_user: CurrentBirthdayReminderUser):
    service.delete_reminder(db, current_user, reminder_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
