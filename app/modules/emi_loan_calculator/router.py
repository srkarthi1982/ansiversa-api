from fastapi import APIRouter, Response, status

from app.modules.emi_loan_calculator import service
from app.modules.emi_loan_calculator.dependencies import CurrentEmiLoanCalculatorUser, EmiLoanCalculatorDB
from app.modules.emi_loan_calculator.schemas import (
    EmiLoanCalculationRequest,
    EmiLoanCalculationResponse,
    EmiLoanDashboardResponse,
    EmiLoanScenarioCreateRequest,
    EmiLoanScenarioDetailResponse,
    EmiLoanScenarioSummaryResponse,
    EmiLoanScenarioUpdateRequest,
)

router = APIRouter()


@router.post("/calculate", response_model=EmiLoanCalculationResponse, operation_id="calculateEmiLoan")
def calculate(payload: EmiLoanCalculationRequest, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    _ = db, current_user
    return service.calculate_loan(payload)


@router.get("/dashboard", response_model=EmiLoanDashboardResponse, operation_id="getEmiLoanCalculatorDashboard")
def get_dashboard(db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.get_dashboard(db, current_user)


@router.get("/scenarios", response_model=list[EmiLoanScenarioSummaryResponse], operation_id="listEmiLoanScenarios")
def list_scenarios(db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.list_scenarios(db, current_user)


@router.post("/scenarios", response_model=EmiLoanScenarioDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createEmiLoanScenario")
def create_scenario(payload: EmiLoanScenarioCreateRequest, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.create_scenario(db, current_user, payload)


@router.get("/scenarios/{scenario_id}", response_model=EmiLoanScenarioDetailResponse, operation_id="getEmiLoanScenario")
def get_scenario(scenario_id: str, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.get_scenario(db, current_user, scenario_id)


@router.put("/scenarios/{scenario_id}", response_model=EmiLoanScenarioDetailResponse, operation_id="updateEmiLoanScenario")
def update_scenario(scenario_id: str, payload: EmiLoanScenarioUpdateRequest, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.update_scenario(db, current_user, scenario_id, payload)


@router.post("/scenarios/{scenario_id}/duplicate", response_model=EmiLoanScenarioDetailResponse, operation_id="duplicateEmiLoanScenario")
def duplicate_scenario(scenario_id: str, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    return service.duplicate_scenario(db, current_user, scenario_id)


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteEmiLoanScenario")
def delete_scenario(scenario_id: str, db: EmiLoanCalculatorDB, current_user: CurrentEmiLoanCalculatorUser):
    service.delete_scenario(db, current_user, scenario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
