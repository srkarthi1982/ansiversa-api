from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.vehicle_maintenance_tracker.db import get_vehicle_maintenance_tracker_db

VehicleMaintenanceDB = Annotated[Session, Depends(get_vehicle_maintenance_tracker_db)]
CurrentVehicleMaintenanceUser = Annotated[User, Depends(get_current_user)]
