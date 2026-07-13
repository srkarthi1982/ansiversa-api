from fastapi import APIRouter, Response, status

from app.modules.subscription_manager import service
from app.modules.subscription_manager.dependencies import CurrentSubscriptionManagerUser, SubscriptionManagerDB
from app.modules.subscription_manager.schemas import (
    SubscriptionManagerCategoryCreateRequest,
    SubscriptionManagerCategoryDetailResponse,
    SubscriptionManagerCategorySummaryResponse,
    SubscriptionManagerCategoryUpdateRequest,
    SubscriptionManagerDashboardResponse,
    SubscriptionManagerRenewalCreateRequest,
    SubscriptionManagerRenewalDetailResponse,
    SubscriptionManagerRenewalSummaryResponse,
    SubscriptionManagerRenewalUpdateRequest,
    SubscriptionManagerSubscriptionActionRequest,
    SubscriptionManagerSubscriptionCreateRequest,
    SubscriptionManagerSubscriptionDetailResponse,
    SubscriptionManagerSubscriptionSummaryResponse,
    SubscriptionManagerSubscriptionUpdateRequest,
)

router = APIRouter()


@router.get("/dashboard", response_model=SubscriptionManagerDashboardResponse, operation_id="getSubscriptionManagerDashboard")
def get_dashboard(db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.get_dashboard(db, current_user)


@router.get("/categories", response_model=list[SubscriptionManagerCategorySummaryResponse], operation_id="listSubscriptionManagerCategories")
def list_categories(db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.list_categories(db, current_user)


@router.post("/categories", response_model=SubscriptionManagerCategoryDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSubscriptionManagerCategory")
def create_category(payload: SubscriptionManagerCategoryCreateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.create_category(db, current_user, payload)


@router.get("/categories/{category_id}", response_model=SubscriptionManagerCategoryDetailResponse, operation_id="getSubscriptionManagerCategory")
def get_category(category_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.get_category(db, current_user, category_id)


@router.put("/categories/{category_id}", response_model=SubscriptionManagerCategoryDetailResponse, operation_id="updateSubscriptionManagerCategory")
def update_category(category_id: str, payload: SubscriptionManagerCategoryUpdateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.update_category(db, current_user, category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSubscriptionManagerCategory")
def delete_category(category_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    service.delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/subscriptions", response_model=list[SubscriptionManagerSubscriptionSummaryResponse], operation_id="listSubscriptionManagerSubscriptions")
def list_subscriptions(db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.list_subscriptions(db, current_user)


@router.post("/subscriptions", response_model=SubscriptionManagerSubscriptionDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSubscriptionManagerSubscription")
def create_subscription(payload: SubscriptionManagerSubscriptionCreateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.create_subscription(db, current_user, payload)


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionManagerSubscriptionDetailResponse, operation_id="getSubscriptionManagerSubscription")
def get_subscription(subscription_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.get_subscription(db, current_user, subscription_id)


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionManagerSubscriptionDetailResponse, operation_id="updateSubscriptionManagerSubscription")
def update_subscription(subscription_id: str, payload: SubscriptionManagerSubscriptionUpdateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.update_subscription(db, current_user, subscription_id, payload)


@router.post("/subscriptions/{subscription_id}/duplicate", response_model=SubscriptionManagerSubscriptionDetailResponse, operation_id="duplicateSubscriptionManagerSubscription")
def duplicate_subscription(subscription_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.duplicate_subscription(db, current_user, subscription_id)


@router.post("/subscriptions/{subscription_id}/pause", response_model=SubscriptionManagerSubscriptionDetailResponse, operation_id="pauseSubscriptionManagerSubscription")
def pause_subscription(subscription_id: str, payload: SubscriptionManagerSubscriptionActionRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.pause_subscription(db, current_user, subscription_id, payload)


@router.post("/subscriptions/{subscription_id}/cancel", response_model=SubscriptionManagerSubscriptionDetailResponse, operation_id="cancelSubscriptionManagerSubscription")
def cancel_subscription(subscription_id: str, payload: SubscriptionManagerSubscriptionActionRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.cancel_subscription(db, current_user, subscription_id, payload)


@router.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSubscriptionManagerSubscription")
def delete_subscription(subscription_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    service.delete_subscription(db, current_user, subscription_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/renewals", response_model=list[SubscriptionManagerRenewalSummaryResponse], operation_id="listSubscriptionManagerRenewals")
def list_renewals(db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.list_renewals(db, current_user)


@router.post("/renewals", response_model=SubscriptionManagerRenewalDetailResponse, status_code=status.HTTP_201_CREATED, operation_id="createSubscriptionManagerRenewal")
def create_renewal(payload: SubscriptionManagerRenewalCreateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.create_renewal(db, current_user, payload)


@router.get("/renewals/{renewal_id}", response_model=SubscriptionManagerRenewalDetailResponse, operation_id="getSubscriptionManagerRenewal")
def get_renewal(renewal_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.get_renewal(db, current_user, renewal_id)


@router.put("/renewals/{renewal_id}", response_model=SubscriptionManagerRenewalDetailResponse, operation_id="updateSubscriptionManagerRenewal")
def update_renewal(renewal_id: str, payload: SubscriptionManagerRenewalUpdateRequest, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    return service.update_renewal(db, current_user, renewal_id, payload)


@router.delete("/renewals/{renewal_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="deleteSubscriptionManagerRenewal")
def delete_renewal(renewal_id: str, db: SubscriptionManagerDB, current_user: CurrentSubscriptionManagerUser):
    service.delete_renewal(db, current_user, renewal_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
