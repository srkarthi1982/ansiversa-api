from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import select

from app.modules.subscription_manager.models import SubscriptionCategory, SubscriptionRecord, SubscriptionRenewal


def get_category(db: Session, category_id: str) -> SubscriptionCategory | None:
    return db.get(SubscriptionCategory, category_id)


def get_subscription(db: Session, subscription_id: str) -> SubscriptionRecord | None:
    return db.get(SubscriptionRecord, subscription_id)


def get_renewal(db: Session, renewal_id: str) -> SubscriptionRenewal | None:
    return db.get(SubscriptionRenewal, renewal_id)


def list_categories(db: Session, owner_id: str) -> list[SubscriptionCategory]:
    return list(
        db.execute(
            select(SubscriptionCategory)
            .options(joinedload(SubscriptionCategory.subscriptions))
            .where(SubscriptionCategory.owner_id == owner_id)
            .order_by(SubscriptionCategory.name.asc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_subscriptions(db: Session, owner_id: str) -> list[SubscriptionRecord]:
    return list(
        db.execute(
            select(SubscriptionRecord)
            .options(joinedload(SubscriptionRecord.category), joinedload(SubscriptionRecord.renewals))
            .where(SubscriptionRecord.owner_id == owner_id)
            .order_by(SubscriptionRecord.next_billing_date.asc(), SubscriptionRecord.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def list_renewals(db: Session, owner_id: str) -> list[SubscriptionRenewal]:
    return list(
        db.execute(
            select(SubscriptionRenewal)
            .options(joinedload(SubscriptionRenewal.subscription).joinedload(SubscriptionRecord.category))
            .where(SubscriptionRenewal.owner_id == owner_id)
            .order_by(SubscriptionRenewal.renewal_date.desc(), SubscriptionRenewal.updated_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def add(db: Session, record: object) -> None:
    db.add(record)


def delete_record(db: Session, record: object) -> None:
    db.delete(record)
