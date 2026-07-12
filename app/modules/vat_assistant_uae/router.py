from fastapi import APIRouter, Response, status

from app.modules.vat_assistant_uae import service
from app.modules.vat_assistant_uae.dependencies import CurrentVatAssistantUser, VatAssistantDB
from app.modules.vat_assistant_uae.schemas import (
    VatDashboardResponse,
    VatRegistrationCreateRequest,
    VatRegistrationDetailResponse,
    VatRegistrationSummaryResponse,
    VatRegistrationUpdateRequest,
    VatReturnCreateRequest,
    VatReturnDetailResponse,
    VatReturnSummaryResponse,
    VatReturnUpdateRequest,
    VatTransactionCreateRequest,
    VatTransactionDetailResponse,
    VatTransactionSummaryResponse,
    VatTransactionUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=VatDashboardResponse, operation_id="getVatAssistantDashboard")
def get_dashboard(db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.get_dashboard(db, current_user)


@router.get("/registrations", response_model=list[VatRegistrationSummaryResponse], operation_id="listVatRegistrations")
def list_registrations(db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.list_registrations(db, current_user)


@router.post("/registrations", response_model=VatRegistrationDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVatRegistration")
def create_registration(payload: VatRegistrationCreateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.create_registration(db, current_user, payload)


@router.get("/registrations/{registration_id}", response_model=VatRegistrationDetailResponse, operation_id="getVatRegistration")
def get_registration(registration_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.get_registration(db, current_user, registration_id)


@router.put("/registrations/{registration_id}", response_model=VatRegistrationDetailResponse, operation_id="updateVatRegistration")
def update_registration(registration_id: str, payload: VatRegistrationUpdateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.update_registration(db, current_user, registration_id, payload)


@router.post("/registrations/{registration_id}/duplicate", response_model=VatRegistrationDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateVatRegistration")
def duplicate_registration(registration_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.duplicate_registration(db, current_user, registration_id)


@router.delete("/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVatRegistration")
def delete_registration(registration_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    service.delete_registration(db, current_user, registration_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/returns", response_model=list[VatReturnSummaryResponse], operation_id="listVatReturns")
def list_returns(db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.list_returns(db, current_user)


@router.post("/returns", response_model=VatReturnDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVatReturn")
def create_return(payload: VatReturnCreateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.create_return(db, current_user, payload)


@router.get("/returns/{return_id}", response_model=VatReturnDetailResponse, operation_id="getVatReturn")
def get_return(return_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.get_return(db, current_user, return_id)


@router.put("/returns/{return_id}", response_model=VatReturnDetailResponse, operation_id="updateVatReturn")
def update_return(return_id: str, payload: VatReturnUpdateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.update_return(db, current_user, return_id, payload)


@router.post("/returns/{return_id}/duplicate", response_model=VatReturnDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateVatReturn")
def duplicate_return(return_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.duplicate_return(db, current_user, return_id)


@router.delete("/returns/{return_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVatReturn")
def delete_return(return_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    service.delete_return(db, current_user, return_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/transactions", response_model=list[VatTransactionSummaryResponse], operation_id="listVatTransactions")
def list_transactions(db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.list_transactions(db, current_user)


@router.post("/transactions", response_model=VatTransactionDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createVatTransaction")
def create_transaction(payload: VatTransactionCreateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.create_transaction(db, current_user, payload)


@router.get("/transactions/{transaction_id}", response_model=VatTransactionDetailResponse, operation_id="getVatTransaction")
def get_transaction(transaction_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.get_transaction(db, current_user, transaction_id)


@router.put("/transactions/{transaction_id}", response_model=VatTransactionDetailResponse, operation_id="updateVatTransaction")
def update_transaction(transaction_id: str, payload: VatTransactionUpdateRequest, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.update_transaction(db, current_user, transaction_id, payload)


@router.post("/transactions/{transaction_id}/duplicate", response_model=VatTransactionDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="duplicateVatTransaction")
def duplicate_transaction(transaction_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    return service.duplicate_transaction(db, current_user, transaction_id)


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteVatTransaction")
def delete_transaction(transaction_id: str, db: VatAssistantDB, current_user: CurrentVatAssistantUser):
    service.delete_transaction(db, current_user, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
