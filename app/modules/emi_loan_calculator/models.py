from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.emi_loan_calculator.db import EmiLoanCalculatorBase


def _uuid() -> str:
    return str(uuid4())


class LoanScenario(EmiLoanCalculatorBase):
    __tablename__ = "LoanScenarios"
    __table_args__ = (
        UniqueConstraint("userId", "name", name="uq_loan_scenarios_owner_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column("userId", String(36), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    loan_amount: Mapped[Decimal] = mapped_column("loanAmount", Numeric(14, 2), nullable=False)
    annual_interest_rate: Mapped[Decimal] = mapped_column("annualInterestRate", Numeric(7, 4), nullable=False)
    duration_value: Mapped[int] = mapped_column("durationValue", Integer, nullable=False)
    duration_unit: Mapped[str] = mapped_column("durationUnit", String(20), default="years", server_default="years", nullable=False)
    repayment_frequency: Mapped[str] = mapped_column("repaymentFrequency", String(20), default="monthly", server_default="monthly", nullable=False)
    start_date: Mapped[str | None] = mapped_column("startDate", String(40), nullable=True)
    processing_fee: Mapped[Decimal] = mapped_column("processingFee", Numeric(14, 2), default=Decimal("0.00"), server_default="0", nullable=False)
    extra_payment: Mapped[Decimal] = mapped_column("extraPayment", Numeric(14, 2), default=Decimal("0.00"), server_default="0", nullable=False)
    currency_code: Mapped[str] = mapped_column("currencyCode", String(3), default="USD", server_default="USD", nullable=False)
    calculated_emi: Mapped[Decimal] = mapped_column("calculatedEmi", Numeric(14, 2), nullable=False)
    total_interest: Mapped[Decimal] = mapped_column("totalInterest", Numeric(14, 2), nullable=False)
    total_repayment: Mapped[Decimal] = mapped_column("totalRepayment", Numeric(14, 2), nullable=False)
    overall_loan_cost: Mapped[Decimal] = mapped_column("overallLoanCost", Numeric(14, 2), nullable=False)
    estimated_payoff_date: Mapped[str | None] = mapped_column("estimatedPayoffDate", String(40), nullable=True)
    installment_count: Mapped[int] = mapped_column("installmentCount", Integer, nullable=False)
    interest_to_principal_ratio: Mapped[Decimal] = mapped_column("interestToPrincipalRatio", Numeric(10, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
