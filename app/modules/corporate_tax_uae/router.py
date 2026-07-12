from fastapi import APIRouter, Response, status

from app.modules.corporate_tax_uae import service
from app.modules.corporate_tax_uae.dependencies import CorporateTaxDB, CurrentCorporateTaxUser
from app.modules.corporate_tax_uae.schemas import (
    CorporateTaxAdjustmentCreateRequest,
    CorporateTaxAdjustmentDetailResponse,
    CorporateTaxAdjustmentSummaryResponse,
    CorporateTaxAdjustmentUpdateRequest,
    CorporateTaxDashboardResponse,
    CorporateTaxObligationCreateRequest,
    CorporateTaxObligationDetailResponse,
    CorporateTaxObligationSummaryResponse,
    CorporateTaxObligationUpdateRequest,
    CorporateTaxPeriodCreateRequest,
    CorporateTaxPeriodDetailResponse,
    CorporateTaxPeriodSummaryResponse,
    CorporateTaxPeriodUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=CorporateTaxDashboardResponse, operation_id="getCorporateTaxDashboard")
def get_dashboard(db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.get_dashboard(db, current_user)


@router.get("/periods", response_model=list[CorporateTaxPeriodSummaryResponse], operation_id="listCorporateTaxPeriods")
def list_periods(db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.list_periods(db, current_user)


@router.post("/periods", response_model=CorporateTaxPeriodDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createCorporateTaxPeriod")
def create_period(payload: CorporateTaxPeriodCreateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.create_period(db, current_user, payload)


@router.get("/periods/{period_id}", response_model=CorporateTaxPeriodDetailResponse, operation_id="getCorporateTaxPeriod")
def get_period(period_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.get_period(db, current_user, period_id)


@router.put("/periods/{period_id}", response_model=CorporateTaxPeriodDetailResponse, operation_id="updateCorporateTaxPeriod")
def update_period(period_id: str, payload: CorporateTaxPeriodUpdateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.update_period(db, current_user, period_id, payload)


@router.post("/periods/{period_id}/duplicate", response_model=CorporateTaxPeriodDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateCorporateTaxPeriod")
def duplicate_period(period_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.duplicate_period(db, current_user, period_id)


@router.delete("/periods/{period_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCorporateTaxPeriod")
def delete_period(period_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    service.delete_period(db, current_user, period_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/adjustments", response_model=list[CorporateTaxAdjustmentSummaryResponse], operation_id="listCorporateTaxAdjustments")
def list_adjustments(db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.list_adjustments(db, current_user)


@router.post("/adjustments", response_model=CorporateTaxAdjustmentDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createCorporateTaxAdjustment")
def create_adjustment(payload: CorporateTaxAdjustmentCreateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.create_adjustment(db, current_user, payload)


@router.get("/adjustments/{adjustment_id}", response_model=CorporateTaxAdjustmentDetailResponse, operation_id="getCorporateTaxAdjustment")
def get_adjustment(adjustment_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.get_adjustment(db, current_user, adjustment_id)


@router.put("/adjustments/{adjustment_id}", response_model=CorporateTaxAdjustmentDetailResponse, operation_id="updateCorporateTaxAdjustment")
def update_adjustment(adjustment_id: str, payload: CorporateTaxAdjustmentUpdateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.update_adjustment(db, current_user, adjustment_id, payload)


@router.delete("/adjustments/{adjustment_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCorporateTaxAdjustment")
def delete_adjustment(adjustment_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    service.delete_adjustment(db, current_user, adjustment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/obligations", response_model=list[CorporateTaxObligationSummaryResponse], operation_id="listCorporateTaxObligations")
def list_obligations(db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.list_obligations(db, current_user)


@router.post("/obligations", response_model=CorporateTaxObligationDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createCorporateTaxObligation")
def create_obligation(payload: CorporateTaxObligationCreateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.create_obligation(db, current_user, payload)


@router.get("/obligations/{obligation_id}", response_model=CorporateTaxObligationDetailResponse, operation_id="getCorporateTaxObligation")
def get_obligation(obligation_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.get_obligation(db, current_user, obligation_id)


@router.put("/obligations/{obligation_id}", response_model=CorporateTaxObligationDetailResponse, operation_id="updateCorporateTaxObligation")
def update_obligation(obligation_id: str, payload: CorporateTaxObligationUpdateRequest, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.update_obligation(db, current_user, obligation_id, payload)


@router.post("/obligations/{obligation_id}/complete", response_model=CorporateTaxObligationDetailResponse, operation_id="completeCorporateTaxObligation")
def complete_obligation(obligation_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    return service.complete_obligation(db, current_user, obligation_id)


@router.delete("/obligations/{obligation_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteCorporateTaxObligation")
def delete_obligation(obligation_id: str, db: CorporateTaxDB, current_user: CurrentCorporateTaxUser):
    service.delete_obligation(db, current_user, obligation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
