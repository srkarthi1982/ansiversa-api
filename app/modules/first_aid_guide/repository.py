from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.modules.first_aid_guide.models import FirstAidCategory, FirstAidGuide, UserGuideBookmark, UserGuideHistory


def add(db: Session, item):
    db.add(item)
    return item


def delete(db: Session, item) -> None:
    db.delete(item)


def list_categories(db: Session) -> list[FirstAidCategory]:
    return list(db.scalars(select(FirstAidCategory).order_by(FirstAidCategory.sort_order, FirstAidCategory.name)))


def get_category(db: Session, item_id: str) -> FirstAidCategory | None:
    return db.get(FirstAidCategory, item_id)


def list_guides(db: Session) -> list[FirstAidGuide]:
    result = db.execute(select(FirstAidGuide).options(joinedload(FirstAidGuide.category)).order_by(FirstAidGuide.display_order, FirstAidGuide.title))
    return list(result.unique().scalars())


def get_guide(db: Session, item_id: str) -> FirstAidGuide | None:
    result = db.execute(select(FirstAidGuide).options(joinedload(FirstAidGuide.category)).where(FirstAidGuide.id == item_id))
    return result.unique().scalars().first()


def guide_counts_by_category(db: Session) -> dict[str, int]:
    rows = db.execute(select(FirstAidGuide.category_id, func.count()).group_by(FirstAidGuide.category_id))
    return {row[0]: row[1] for row in rows}


def count_guides_for_category(db: Session, category_id: str) -> int:
    return db.scalar(select(func.count()).select_from(FirstAidGuide).where(FirstAidGuide.category_id == category_id)) or 0


def bookmark_ids(db: Session, owner_id: str) -> set[str]:
    return set(db.scalars(select(UserGuideBookmark.guide_id).where(UserGuideBookmark.owner_id == owner_id)))


def get_bookmark(db: Session, owner_id: str, guide_id: str) -> UserGuideBookmark | None:
    return db.scalar(select(UserGuideBookmark).where(UserGuideBookmark.owner_id == owner_id, UserGuideBookmark.guide_id == guide_id))


def history_counts(db: Session, owner_id: str) -> dict[str, int]:
    rows = db.execute(select(UserGuideHistory.guide_id, func.count()).where(UserGuideHistory.owner_id == owner_id).group_by(UserGuideHistory.guide_id))
    return {row[0]: row[1] for row in rows}


def recent_history_guide_ids(db: Session, owner_id: str, limit: int = 8) -> list[str]:
    rows = db.execute(select(UserGuideHistory.guide_id, func.max(UserGuideHistory.viewed_at).label("last_viewed")).where(UserGuideHistory.owner_id == owner_id).group_by(UserGuideHistory.guide_id).order_by(func.max(UserGuideHistory.viewed_at).desc()).limit(limit))
    return [row[0] for row in rows]


def total_history(db: Session, owner_id: str) -> int:
    return db.scalar(select(func.count()).select_from(UserGuideHistory).where(UserGuideHistory.owner_id == owner_id)) or 0
