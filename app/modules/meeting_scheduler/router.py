from fastapi import APIRouter, Query, Response, status

from app.modules.meeting_scheduler import service
from app.modules.meeting_scheduler.dependencies import CurrentMeetingSchedulerUser, MeetingSchedulerDB
from app.modules.meeting_scheduler.schemas import MeetingPeriod, MeetingSchedulerAgendaItemCreateRequest, MeetingSchedulerAgendaItemResponse, MeetingSchedulerAgendaItemUpdateRequest, MeetingSchedulerDashboardResponse, MeetingSchedulerMeetingCreateRequest, MeetingSchedulerMeetingDetailResponse, MeetingSchedulerMeetingListResponse, MeetingSchedulerMeetingResponse, MeetingSchedulerMeetingUpdateRequest, MeetingSchedulerParticipantCreateRequest, MeetingSchedulerParticipantResponse, MeetingSchedulerParticipantUpdateRequest, MeetingStatus

router = APIRouter()


@router.get("/dashboard", response_model=MeetingSchedulerDashboardResponse, operation_id="getMeetingSchedulerDashboard")
def get_dashboard(db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.dashboard(db, current_user)


@router.get("/meetings", response_model=MeetingSchedulerMeetingListResponse, operation_id="listMeetingSchedulerMeetings")
def list_meetings(db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser, q: str | None = None, status_filter: MeetingStatus | None = Query(default=None, alias="status"), period: MeetingPeriod = "all", page: int = Query(default=1, ge=1), page_size: int = Query(default=20, alias="pageSize", ge=1, le=100)):
    return service.list_meetings(db, current_user, q, status_filter, period, page, page_size)


@router.post("/meetings", response_model=MeetingSchedulerMeetingResponse, status_code=201, operation_id="createMeetingSchedulerMeeting")
def create_meeting(payload: MeetingSchedulerMeetingCreateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.create_meeting(db, current_user, payload)


@router.get("/meetings/{meeting_id}", response_model=MeetingSchedulerMeetingDetailResponse, operation_id="getMeetingSchedulerMeeting")
def get_meeting(meeting_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.get_meeting(db, current_user, meeting_id)


@router.put("/meetings/{meeting_id}", response_model=MeetingSchedulerMeetingResponse, operation_id="updateMeetingSchedulerMeeting")
def update_meeting(meeting_id: str, payload: MeetingSchedulerMeetingUpdateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.update_meeting(db, current_user, meeting_id, payload)


@router.delete("/meetings/{meeting_id}", status_code=204, operation_id="deleteMeetingSchedulerMeeting")
def delete_meeting(meeting_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): service.delete_meeting(db, current_user, meeting_id); return Response(status_code=204)


@router.post("/meetings/{meeting_id}/participants", response_model=MeetingSchedulerParticipantResponse, status_code=201, operation_id="createMeetingSchedulerParticipant")
def create_participant(meeting_id: str, payload: MeetingSchedulerParticipantCreateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.create_participant(db, current_user, meeting_id, payload)


@router.get("/meetings/{meeting_id}/participants", response_model=list[MeetingSchedulerParticipantResponse], operation_id="listMeetingSchedulerParticipants")
def list_participants(meeting_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.list_participants(db, current_user, meeting_id)


@router.put("/meetings/{meeting_id}/participants/{participant_id}", response_model=MeetingSchedulerParticipantResponse, operation_id="updateMeetingSchedulerParticipant")
def update_participant(meeting_id: str, participant_id: str, payload: MeetingSchedulerParticipantUpdateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.update_participant(db, current_user, meeting_id, participant_id, payload)


@router.delete("/meetings/{meeting_id}/participants/{participant_id}", status_code=204, operation_id="deleteMeetingSchedulerParticipant")
def delete_participant(meeting_id: str, participant_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): service.delete_participant(db, current_user, meeting_id, participant_id); return Response(status_code=204)


@router.post("/meetings/{meeting_id}/agenda-items", response_model=MeetingSchedulerAgendaItemResponse, status_code=201, operation_id="createMeetingSchedulerAgendaItem")
def create_agenda_item(meeting_id: str, payload: MeetingSchedulerAgendaItemCreateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.create_agenda_item(db, current_user, meeting_id, payload)


@router.get("/meetings/{meeting_id}/agenda-items", response_model=list[MeetingSchedulerAgendaItemResponse], operation_id="listMeetingSchedulerAgendaItems")
def list_agenda_items(meeting_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.list_agenda_items(db, current_user, meeting_id)


@router.put("/meetings/{meeting_id}/agenda-items/{item_id}", response_model=MeetingSchedulerAgendaItemResponse, operation_id="updateMeetingSchedulerAgendaItem")
def update_agenda_item(meeting_id: str, item_id: str, payload: MeetingSchedulerAgendaItemUpdateRequest, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): return service.update_agenda_item(db, current_user, meeting_id, item_id, payload)


@router.delete("/meetings/{meeting_id}/agenda-items/{item_id}", status_code=204, operation_id="deleteMeetingSchedulerAgendaItem")
def delete_agenda_item(meeting_id: str, item_id: str, db: MeetingSchedulerDB, current_user: CurrentMeetingSchedulerUser): service.delete_agenda_item(db, current_user, meeting_id, item_id); return Response(status_code=204)
