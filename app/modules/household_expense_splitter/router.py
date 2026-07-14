from fastapi import APIRouter, Query, Response, status

from app.modules.household_expense_splitter import service
from app.modules.household_expense_splitter.dependencies import CurrentHouseholdExpenseSplitterUser, HouseholdExpenseSplitterDB
from app.modules.household_expense_splitter.schemas import (
    ArchiveFilter,
    DashboardResponse,
    ExpenseCreateRequest,
    ExpenseDetailResponse,
    ExpenseSort,
    ExpenseSummaryResponse,
    ExpenseUpdateRequest,
    InsightsResponse,
    MemberCreateRequest,
    MemberResponse,
    MemberUpdateRequest,
    SettlementCreateRequest,
    SettlementResponse,
    SettlementUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, operation_id="getHouseholdExpenseSplitterDashboard")
def get_dashboard(db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.get_dashboard(db, current_user)


@router.get("/insights", response_model=InsightsResponse, operation_id="getHouseholdExpenseSplitterInsights")
def get_insights(db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.get_insights(db, current_user)


@router.get("/members", response_model=list[MemberResponse], operation_id="listHouseholdExpenseSplitterMembers")
def list_members(db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.list_members(db, current_user)


@router.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED, operation_id="createHouseholdExpenseSplitterMember")
def create_member(payload: MemberCreateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.create_member(db, current_user, payload)


@router.put("/members/{member_id}", response_model=MemberResponse, operation_id="updateHouseholdExpenseSplitterMember")
def update_member(member_id: str, payload: MemberUpdateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.update_member(db, current_user, member_id, payload)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHouseholdExpenseSplitterMember")
def delete_member(member_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    service.delete_member(db, current_user, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/expenses", response_model=list[ExpenseSummaryResponse], operation_id="listHouseholdExpenseSplitterExpenses")
def list_expenses(
    db: HouseholdExpenseSplitterDB,
    current_user: CurrentHouseholdExpenseSplitterUser,
    q: str | None = Query(default=None),
    member_id: str | None = Query(default=None, alias="memberId"),
    category: str | None = Query(default=None),
    archive_filter: ArchiveFilter = Query(default="active", alias="archiveFilter"),
    split_method: str | None = Query(default=None, alias="splitMethod"),
    expense_date: str | None = Query(default=None, alias="expenseDate"),
    sort_by: ExpenseSort = Query(default="newest", alias="sortBy"),
):
    return service.list_expenses(db, current_user, q, member_id, category, archive_filter, split_method, expense_date, sort_by)


@router.post("/expenses", response_model=ExpenseDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createHouseholdExpenseSplitterExpense")
def create_expense(payload: ExpenseCreateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.create_expense(db, current_user, payload)


@router.get("/expenses/{expense_id}", response_model=ExpenseDetailResponse, operation_id="getHouseholdExpenseSplitterExpense")
def get_expense(expense_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.get_expense(db, current_user, expense_id)


@router.put("/expenses/{expense_id}", response_model=ExpenseDetailResponse, operation_id="updateHouseholdExpenseSplitterExpense")
def update_expense(expense_id: str, payload: ExpenseUpdateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.update_expense(db, current_user, expense_id, payload)


@router.post("/expenses/{expense_id}/archive", response_model=ExpenseDetailResponse, operation_id="archiveHouseholdExpenseSplitterExpense")
def archive_expense(expense_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.set_expense_archived(db, current_user, expense_id, True)


@router.post("/expenses/{expense_id}/restore", response_model=ExpenseDetailResponse, operation_id="restoreHouseholdExpenseSplitterExpense")
def restore_expense(expense_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.set_expense_archived(db, current_user, expense_id, False)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHouseholdExpenseSplitterExpense")
def delete_expense(expense_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    service.delete_expense(db, current_user, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/settlements", response_model=list[SettlementResponse], operation_id="listHouseholdExpenseSplitterSettlements")
def list_settlements(db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.list_settlements(db, current_user)


@router.post("/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED, operation_id="createHouseholdExpenseSplitterSettlement")
def create_settlement(payload: SettlementCreateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.create_settlement(db, current_user, payload)


@router.put("/settlements/{settlement_id}", response_model=SettlementResponse, operation_id="updateHouseholdExpenseSplitterSettlement")
def update_settlement(settlement_id: str, payload: SettlementUpdateRequest, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    return service.update_settlement(db, current_user, settlement_id, payload)


@router.delete("/settlements/{settlement_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteHouseholdExpenseSplitterSettlement")
def delete_settlement(settlement_id: str, db: HouseholdExpenseSplitterDB, current_user: CurrentHouseholdExpenseSplitterUser):
    service.delete_settlement(db, current_user, settlement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
