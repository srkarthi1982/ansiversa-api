from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.vat_assistant_uae import repository
from app.modules.vat_assistant_uae.models import VatRegistration, VatReturn, VatTransaction
from app.modules.vat_assistant_uae.schemas import (
    VatBreakdownResponse,
    VatDashboardResponse,
    VatMoneyResponse,
    VatPeriodSummaryResponse,
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

PREVIEW_LENGTH = 220
DISCLAIMER = (
    "VAT Assistant UAE stores user-entered planning and record-keeping information. "
    "It does not replace official UAE Federal Tax Authority filing requirements or professional tax advice."
)


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_registration(db: Session, user: User, registration_id: str) -> VatRegistration:
    registration = repository.get_registration(db, registration_id)
    if not registration or registration.owner_id != user.id:
        _not_found("VAT registration was not found.")
    return registration


def _get_owned_return(db: Session, user: User, return_id: str) -> VatReturn:
    vat_return = repository.get_return(db, return_id)
    if not vat_return or vat_return.owner_id != user.id:
        _not_found("VAT return was not found.")
    return vat_return


def _get_owned_transaction(db: Session, user: User, transaction_id: str) -> VatTransaction:
    transaction = repository.get_transaction(db, transaction_id)
    if not transaction or transaction.owner_id != user.id:
        _not_found("VAT transaction was not found.")
    return transaction


def _registration_summary(registration: VatRegistration) -> VatRegistrationSummaryResponse:
    return VatRegistrationSummaryResponse(
        id=registration.id,
        business_name=registration.business_name,
        trn=registration.trn,
        registration_type=registration.registration_type,
        registration_date=registration.registration_date,
        vat_period=registration.vat_period,
        status=registration.status,
        country=registration.country,
        return_count=len(registration.returns),
        transaction_count=len(registration.transactions),
        notes_preview=_preview(registration.notes),
        created_at=registration.created_at,
        updated_at=registration.updated_at,
    )


def _registration_detail(registration: VatRegistration) -> VatRegistrationDetailResponse:
    return VatRegistrationDetailResponse(**_registration_summary(registration).model_dump(), notes=registration.notes)


def _return_summary(vat_return: VatReturn) -> VatReturnSummaryResponse:
    return VatReturnSummaryResponse(
        id=vat_return.id,
        registration_id=vat_return.registration_id,
        business_name=vat_return.registration.business_name if vat_return.registration else "VAT registration",
        vat_period=vat_return.vat_period,
        filing_due_date=vat_return.filing_due_date,
        output_vat=vat_return.output_vat,
        input_vat=vat_return.input_vat,
        payable_vat=vat_return.payable_vat,
        refund_amount=vat_return.refund_amount,
        filing_status=vat_return.filing_status,
        submission_date=vat_return.submission_date,
        currency_code=vat_return.currency_code,
        notes_preview=_preview(vat_return.notes),
        created_at=vat_return.created_at,
        updated_at=vat_return.updated_at,
    )


def _return_detail(vat_return: VatReturn) -> VatReturnDetailResponse:
    return VatReturnDetailResponse(**_return_summary(vat_return).model_dump(), notes=vat_return.notes)


def _transaction_summary(transaction: VatTransaction) -> VatTransactionSummaryResponse:
    return VatTransactionSummaryResponse(
        id=transaction.id,
        registration_id=transaction.registration_id,
        business_name=transaction.registration.business_name if transaction.registration else "VAT registration",
        return_id=transaction.return_id,
        return_period=transaction.vat_return.vat_period if transaction.vat_return else None,
        transaction_date=transaction.transaction_date,
        invoice_number=transaction.invoice_number,
        counterparty=transaction.counterparty,
        transaction_type=transaction.transaction_type,
        taxable_amount=transaction.taxable_amount,
        vat_rate=transaction.vat_rate,
        vat_amount=transaction.vat_amount,
        currency_code=transaction.currency_code,
        notes_preview=_preview(transaction.notes),
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )


def _transaction_detail(transaction: VatTransaction) -> VatTransactionDetailResponse:
    return VatTransactionDetailResponse(**_transaction_summary(transaction).model_dump(), notes=transaction.notes)


def _money_items(values: dict[str, float]) -> list[VatMoneyResponse]:
    return [VatMoneyResponse(currency_code=currency, amount=round(amount, 2)) for currency, amount in sorted(values.items())]


def list_registrations(db: Session, user: User) -> list[VatRegistrationSummaryResponse]:
    return [_registration_summary(registration) for registration in repository.list_registrations(db, user.id)]


def create_registration(db: Session, user: User, payload: VatRegistrationCreateRequest) -> VatRegistrationDetailResponse:
    registration = VatRegistration(owner_id=user.id, **payload.model_dump())
    repository.add(db, registration)
    db.commit()
    db.refresh(registration)
    return _registration_detail(registration)


def get_registration(db: Session, user: User, registration_id: str) -> VatRegistrationDetailResponse:
    return _registration_detail(_get_owned_registration(db, user, registration_id))


def update_registration(db: Session, user: User, registration_id: str, payload: VatRegistrationUpdateRequest) -> VatRegistrationDetailResponse:
    registration = _get_owned_registration(db, user, registration_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(registration, field, value)
    db.commit()
    db.refresh(registration)
    return _registration_detail(registration)


def duplicate_registration(db: Session, user: User, registration_id: str) -> VatRegistrationDetailResponse:
    source = _get_owned_registration(db, user, registration_id)
    copy = VatRegistration(
        owner_id=user.id,
        business_name=f"{source.business_name} copy",
        trn=source.trn,
        registration_type=source.registration_type,
        registration_date=source.registration_date,
        vat_period=source.vat_period,
        status="draft",
        country=source.country,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _registration_detail(copy)


def delete_registration(db: Session, user: User, registration_id: str) -> None:
    registration = _get_owned_registration(db, user, registration_id)
    repository.delete_record(db, registration)
    db.commit()


def list_returns(db: Session, user: User) -> list[VatReturnSummaryResponse]:
    return [_return_summary(vat_return) for vat_return in repository.list_returns(db, user.id)]


def create_return(db: Session, user: User, payload: VatReturnCreateRequest) -> VatReturnDetailResponse:
    data = payload.model_dump()
    _get_owned_registration(db, user, data["registration_id"])
    vat_return = VatReturn(owner_id=user.id, **data)
    repository.add(db, vat_return)
    db.commit()
    db.refresh(vat_return)
    return _return_detail(vat_return)


def get_return(db: Session, user: User, return_id: str) -> VatReturnDetailResponse:
    return _return_detail(_get_owned_return(db, user, return_id))


def update_return(db: Session, user: User, return_id: str, payload: VatReturnUpdateRequest) -> VatReturnDetailResponse:
    vat_return = _get_owned_return(db, user, return_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vat_return, field, value)
    db.commit()
    db.refresh(vat_return)
    return _return_detail(vat_return)


def duplicate_return(db: Session, user: User, return_id: str) -> VatReturnDetailResponse:
    source = _get_owned_return(db, user, return_id)
    copy = VatReturn(
        owner_id=user.id,
        registration_id=source.registration_id,
        vat_period=f"{source.vat_period} copy",
        filing_due_date=source.filing_due_date,
        output_vat=source.output_vat,
        input_vat=source.input_vat,
        payable_vat=source.payable_vat,
        refund_amount=source.refund_amount,
        filing_status="draft",
        submission_date=None,
        currency_code=source.currency_code,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _return_detail(copy)


def delete_return(db: Session, user: User, return_id: str) -> None:
    vat_return = _get_owned_return(db, user, return_id)
    repository.delete_record(db, vat_return)
    db.commit()


def list_transactions(db: Session, user: User) -> list[VatTransactionSummaryResponse]:
    return [_transaction_summary(transaction) for transaction in repository.list_transactions(db, user.id)]


def create_transaction(db: Session, user: User, payload: VatTransactionCreateRequest) -> VatTransactionDetailResponse:
    data = payload.model_dump()
    _get_owned_registration(db, user, data["registration_id"])
    if data.get("return_id"):
        vat_return = _get_owned_return(db, user, data["return_id"])
        if vat_return.registration_id != data["registration_id"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VAT return must belong to the selected registration.")
    transaction = VatTransaction(owner_id=user.id, **data)
    repository.add(db, transaction)
    db.commit()
    db.refresh(transaction)
    return _transaction_detail(transaction)


def get_transaction(db: Session, user: User, transaction_id: str) -> VatTransactionDetailResponse:
    return _transaction_detail(_get_owned_transaction(db, user, transaction_id))


def update_transaction(db: Session, user: User, transaction_id: str, payload: VatTransactionUpdateRequest) -> VatTransactionDetailResponse:
    transaction = _get_owned_transaction(db, user, transaction_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("return_id"):
        vat_return = _get_owned_return(db, user, data["return_id"])
        if vat_return.registration_id != transaction.registration_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VAT return must belong to the transaction registration.")
    for field, value in data.items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return _transaction_detail(transaction)


def duplicate_transaction(db: Session, user: User, transaction_id: str) -> VatTransactionDetailResponse:
    source = _get_owned_transaction(db, user, transaction_id)
    copy = VatTransaction(
        owner_id=user.id,
        registration_id=source.registration_id,
        return_id=source.return_id,
        transaction_date=source.transaction_date,
        invoice_number=f"{source.invoice_number or 'Invoice'} copy",
        counterparty=source.counterparty,
        transaction_type=source.transaction_type,
        taxable_amount=source.taxable_amount,
        vat_rate=source.vat_rate,
        vat_amount=source.vat_amount,
        currency_code=source.currency_code,
        notes=source.notes,
    )
    repository.add(db, copy)
    db.commit()
    db.refresh(copy)
    return _transaction_detail(copy)


def delete_transaction(db: Session, user: User, transaction_id: str) -> None:
    transaction = _get_owned_transaction(db, user, transaction_id)
    repository.delete_record(db, transaction)
    db.commit()


def get_dashboard(db: Session, user: User) -> VatDashboardResponse:
    raw_registrations = repository.list_registrations(db, user.id)
    raw_returns = repository.list_returns(db, user.id)
    raw_transactions = repository.list_transactions(db, user.id)
    registrations = [_registration_summary(registration) for registration in raw_registrations]
    returns = [_return_summary(vat_return) for vat_return in raw_returns]
    transactions = [_transaction_summary(transaction) for transaction in raw_transactions]

    output_vat: dict[str, float] = defaultdict(float)
    input_vat: dict[str, float] = defaultdict(float)
    net_vat: dict[str, float] = defaultdict(float)
    by_period: dict[str, dict[str, float]] = defaultdict(lambda: {"output": 0, "input": 0, "net": 0, "count": 0})
    by_rate: dict[str, dict[str, float]] = defaultdict(lambda: {"amount": 0, "count": 0})

    for vat_return in raw_returns:
        output_vat[vat_return.currency_code] += vat_return.output_vat
        input_vat[vat_return.currency_code] += vat_return.input_vat
        net_vat[vat_return.currency_code] += vat_return.payable_vat - vat_return.refund_amount
        period = by_period[vat_return.vat_period]
        period["output"] += vat_return.output_vat
        period["input"] += vat_return.input_vat
        period["net"] += vat_return.payable_vat - vat_return.refund_amount
        period["count"] += 1

    for transaction in raw_transactions:
        rate = f"{transaction.vat_rate:g}%"
        by_rate[rate]["amount"] += transaction.vat_amount
        by_rate[rate]["count"] += 1

    return VatDashboardResponse(
        registrations=registrations,
        returns=returns,
        transactions=transactions,
        total_registrations=len(registrations),
        active_registrations=len([registration for registration in registrations if registration.status == "active"]),
        filed_returns=len([vat_return for vat_return in returns if vat_return.filing_status == "filed_externally"]),
        pending_returns=len([vat_return for vat_return in returns if vat_return.filing_status in {"draft", "ready_for_review", "payment_pending", "overdue"}]),
        total_output_vat_by_currency=_money_items(output_vat),
        total_input_vat_by_currency=_money_items(input_vat),
        net_vat_payable_by_currency=_money_items(net_vat),
        vat_by_period=[
            VatPeriodSummaryResponse(
                vat_period=label,
                output_vat=round(values["output"], 2),
                input_vat=round(values["input"], 2),
                net_vat_payable=round(values["net"], 2),
                return_count=int(values["count"]),
            )
            for label, values in sorted(by_period.items())
        ],
        vat_by_rate=[
            VatBreakdownResponse(label=label, amount=round(values["amount"], 2), count=int(values["count"]))
            for label, values in sorted(by_rate.items())
        ],
        recent_activity=transactions[:6],
        disclaimer=DISCLAIMER,
    )
