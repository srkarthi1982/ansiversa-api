from fastapi import APIRouter, Response, status

from app.modules.vehicle_maintenance_tracker import service
from app.modules.vehicle_maintenance_tracker.dependencies import CurrentVehicleMaintenanceUser, VehicleMaintenanceDB
from app.modules.vehicle_maintenance_tracker.schemas import (
    VehicleMaintenanceDashboardResponse,
    VehicleMaintenanceRecordCreateRequest,
    VehicleMaintenanceRecordDetailResponse,
    VehicleMaintenanceRecordSummaryResponse,
    VehicleMaintenanceRecordUpdateRequest,
    VehicleMaintenanceReminderCreateRequest,
    VehicleMaintenanceReminderDetailResponse,
    VehicleMaintenanceReminderSummaryResponse,
    VehicleMaintenanceReminderUpdateRequest,
    VehicleMaintenanceVehicleCreateRequest,
    VehicleMaintenanceVehicleDetailResponse,
    VehicleMaintenanceVehicleDuplicateRequest,
    VehicleMaintenanceVehicleSummaryResponse,
    VehicleMaintenanceVehicleUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=VehicleMaintenanceDashboardResponse, operation_id="getVehicleMaintenanceDashboard")
def get_dashboard(db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.get_dashboard(db, current_user)


@router.get("/vehicles", response_model=list[VehicleMaintenanceVehicleSummaryResponse], operation_id="listVehicleMaintenanceVehicles")
def list_vehicles(db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.list_vehicles(db, current_user)


@router.post("/vehicles", response_model=VehicleMaintenanceVehicleDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleMaintenanceVehicle")
def create_vehicle(payload: VehicleMaintenanceVehicleCreateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.create_vehicle(db, current_user, payload)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleMaintenanceVehicleDetailResponse, operation_id="getVehicleMaintenanceVehicle")
def get_vehicle(vehicle_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.get_vehicle(db, current_user, vehicle_id)


@router.put("/vehicles/{vehicle_id}", response_model=VehicleMaintenanceVehicleDetailResponse, operation_id="updateVehicleMaintenanceVehicle")
def update_vehicle(vehicle_id: str, payload: VehicleMaintenanceVehicleUpdateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.update_vehicle(db, current_user, vehicle_id, payload)


@router.post("/vehicles/{vehicle_id}/duplicate", response_model=VehicleMaintenanceVehicleDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateVehicleMaintenanceVehicle")
def duplicate_vehicle(vehicle_id: str, payload: VehicleMaintenanceVehicleDuplicateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.duplicate_vehicle(db, current_user, vehicle_id, payload)


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleMaintenanceVehicle")
def delete_vehicle(vehicle_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    service.delete_vehicle(db, current_user, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/records", response_model=list[VehicleMaintenanceRecordSummaryResponse], operation_id="listVehicleMaintenanceRecords")
def list_records(db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.list_records(db, current_user)


@router.post("/records", response_model=VehicleMaintenanceRecordDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleMaintenanceRecord")
def create_record(payload: VehicleMaintenanceRecordCreateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.create_record(db, current_user, payload)


@router.get("/records/{record_id}", response_model=VehicleMaintenanceRecordDetailResponse, operation_id="getVehicleMaintenanceRecord")
def get_record(record_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.get_record(db, current_user, record_id)


@router.put("/records/{record_id}", response_model=VehicleMaintenanceRecordDetailResponse, operation_id="updateVehicleMaintenanceRecord")
def update_record(record_id: str, payload: VehicleMaintenanceRecordUpdateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.update_record(db, current_user, record_id, payload)


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleMaintenanceRecord")
def delete_record(record_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    service.delete_record(db, current_user, record_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reminders", response_model=list[VehicleMaintenanceReminderSummaryResponse], operation_id="listVehicleMaintenanceReminders")
def list_reminders(db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.list_reminders(db, current_user)


@router.post("/reminders", response_model=VehicleMaintenanceReminderDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVehicleMaintenanceReminder")
def create_reminder(payload: VehicleMaintenanceReminderCreateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.create_reminder(db, current_user, payload)


@router.get("/reminders/{reminder_id}", response_model=VehicleMaintenanceReminderDetailResponse, operation_id="getVehicleMaintenanceReminder")
def get_reminder(reminder_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.get_reminder(db, current_user, reminder_id)


@router.put("/reminders/{reminder_id}", response_model=VehicleMaintenanceReminderDetailResponse, operation_id="updateVehicleMaintenanceReminder")
def update_reminder(reminder_id: str, payload: VehicleMaintenanceReminderUpdateRequest, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.update_reminder(db, current_user, reminder_id, payload)


@router.post("/reminders/{reminder_id}/complete", response_model=VehicleMaintenanceReminderDetailResponse, operation_id="completeVehicleMaintenanceReminder")
def complete_reminder(reminder_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    return service.complete_reminder(db, current_user, reminder_id)


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVehicleMaintenanceReminder")
def delete_reminder(reminder_id: str, db: VehicleMaintenanceDB, current_user: CurrentVehicleMaintenanceUser):
    service.delete_reminder(db, current_user, reminder_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
