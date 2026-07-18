from datetime import date
from math import ceil

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from .models import TravelActivity, TravelActivityCategory, TravelItinerary, TravelItineraryDay
from .schemas import (
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    ItineraryCreate,
    ItineraryDayCreate,
    ItineraryDayResponse,
    ItineraryDayUpdate,
    ItineraryDetail,
    ItineraryList,
    ItineraryStatus,
    ItinerarySummary,
    ItineraryUpdate,
    TravelCategoryCreate,
    TravelCategoryList,
    TravelCategoryResponse,
    TravelCategoryUpdate,
    TravelDashboard,
)


def fail(code: int, message: str):
    raise HTTPException(code, message)


def user_id(user) -> str:
    return str(user.id)


def owned_itinerary(db: Session, user, itinerary_id: str) -> TravelItinerary:
    itinerary = db.scalar(
        select(TravelItinerary)
        .where(TravelItinerary.id == itinerary_id, TravelItinerary.user_id == user_id(user))
        .options(
            selectinload(TravelItinerary.days)
            .selectinload(TravelItineraryDay.activities)
            .selectinload(TravelActivity.category),
        ),
    )
    if not itinerary:
        fail(404, "Itinerary not found.")
    return itinerary


def owned_day(db: Session, user, itinerary_id: str, day_id: str) -> TravelItineraryDay:
    itinerary = owned_itinerary(db, user, itinerary_id)
    for day in itinerary.days:
        if day.id == day_id:
            return day
    fail(404, "Itinerary day not found.")


def owned_activity(
    db: Session,
    user,
    itinerary_id: str,
    day_id: str,
    activity_id: str,
) -> TravelActivity:
    day = owned_day(db, user, itinerary_id, day_id)
    for activity in day.activities:
        if activity.id == activity_id:
            return activity
    fail(404, "Activity not found.")


def owned_category(db: Session, user, category_id: str) -> TravelActivityCategory:
    category = db.scalar(
        select(TravelActivityCategory).where(
            TravelActivityCategory.id == category_id,
            TravelActivityCategory.user_id == user_id(user),
        ),
    )
    if not category:
        fail(404, "Category not found.")
    return category


def category_for(db: Session, user, category_id: str | None):
    if not category_id:
        return None
    return owned_category(db, user, category_id)


def ensure_day_within_trip(itinerary: TravelItinerary, day_date: date) -> None:
    if day_date < itinerary.start_date or day_date > itinerary.end_date:
        fail(422, "Day date must be inside the itinerary date range.")


def ensure_unique_trip_name(db: Session, user, name: str, itinerary_id: str | None = None) -> None:
    duplicate = db.scalar(
        select(TravelItinerary).where(
            TravelItinerary.user_id == user_id(user),
            func.lower(TravelItinerary.name) == name.lower(),
            TravelItinerary.id != (itinerary_id or ""),
        ),
    )
    if duplicate:
        fail(409, "Itinerary name already exists.")


def activity_response(activity: TravelActivity) -> ActivityResponse:
    category = activity.category
    return ActivityResponse(
        id=activity.id,
        category_id=activity.category_id,
        category_name=category.name if category else None,
        category_color=category.color if category else None,
        title=activity.title,
        start_time=activity.start_time,
        end_time=activity.end_time,
        location=activity.location,
        booking_reference=activity.booking_reference,
        notes=activity.notes,
        sort_order=activity.sort_order,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
    )


def day_response(day: TravelItineraryDay, include_activities: bool = True) -> ItineraryDayResponse:
    activities = sorted(day.activities, key=lambda a: (a.start_time is None, a.start_time, a.sort_order, a.created_at))
    return ItineraryDayResponse(
        id=day.id,
        day_date=day.day_date,
        title=day.title,
        notes=day.notes,
        sort_order=day.sort_order,
        activity_count=len(day.activities),
        activities=[activity_response(activity) for activity in activities] if include_activities else [],
        created_at=day.created_at,
        updated_at=day.updated_at,
    )


def summary(itinerary: TravelItinerary) -> ItinerarySummary:
    days = list(itinerary.days)
    activities = [activity for day in days for activity in day.activities]
    next_activity = next(
        (
            activity.title
            for day in sorted(days, key=lambda d: d.day_date)
            for activity in sorted(day.activities, key=lambda a: (a.start_time is None, a.start_time, a.sort_order, a.created_at))
        ),
        None,
    )
    return ItinerarySummary(
        id=itinerary.id,
        name=itinerary.name,
        destination=itinerary.destination,
        start_date=itinerary.start_date,
        end_date=itinerary.end_date,
        status=itinerary.status,
        purpose=itinerary.purpose,
        day_count=len(days),
        activity_count=len(activities),
        next_activity=next_activity,
        created_at=itinerary.created_at,
        updated_at=itinerary.updated_at,
    )


def detail(itinerary: TravelItinerary) -> ItineraryDetail:
    base = summary(itinerary)
    days = sorted(itinerary.days, key=lambda day: (day.day_date, day.sort_order, day.created_at))
    return ItineraryDetail(
        **base.model_dump(),
        notes=itinerary.notes,
        days=[day_response(day) for day in days],
    )


def category_response(db: Session, category: TravelActivityCategory) -> TravelCategoryResponse:
    count = db.scalar(
        select(func.count()).select_from(TravelActivity).where(TravelActivity.category_id == category.id),
    ) or 0
    return TravelCategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        sort_order=category.sort_order,
        activity_count=count,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def save_itinerary(db: Session, user, payload: ItineraryCreate | ItineraryUpdate, itinerary_id: str | None = None) -> ItineraryDetail:
    itinerary = owned_itinerary(db, user, itinerary_id) if itinerary_id else TravelItinerary(user_id=user_id(user))
    ensure_unique_trip_name(db, user, payload.name, itinerary_id)
    for day in itinerary.days:
        if day.day_date < payload.start_date or day.day_date > payload.end_date:
            fail(422, "Existing itinerary days must stay inside the date range.")
    for key, value in payload.model_dump().items():
        setattr(itinerary, key, value)
    if not itinerary_id:
        db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return get_itinerary(db, user, itinerary.id)


def get_itinerary(db: Session, user, itinerary_id: str) -> ItineraryDetail:
    return detail(owned_itinerary(db, user, itinerary_id))


def list_itineraries(
    db: Session,
    user,
    q: str | None = None,
    status: ItineraryStatus | None = None,
    destination: str | None = None,
    starts_from: date | None = None,
    starts_to: date | None = None,
    page: int = 1,
    page_size: int = 12,
) -> ItineraryList:
    if starts_from and starts_to and starts_from > starts_to:
        fail(422, "Starts-from date cannot be after starts-to date.")
    stmt = (
        select(TravelItinerary)
        .where(TravelItinerary.user_id == user_id(user))
        .options(selectinload(TravelItinerary.days).selectinload(TravelItineraryDay.activities))
    )
    term = (q or "").strip()
    if term:
        stmt = stmt.where(
            or_(
                TravelItinerary.name.ilike(f"%{term}%"),
                TravelItinerary.destination.ilike(f"%{term}%"),
                TravelItinerary.notes.ilike(f"%{term}%"),
                TravelItinerary.purpose.ilike(f"%{term}%"),
            ),
        )
    if status:
        stmt = stmt.where(TravelItinerary.status == status)
    if destination:
        stmt = stmt.where(TravelItinerary.destination.ilike(f"%{destination.strip()}%"))
    if starts_from:
        stmt = stmt.where(TravelItinerary.start_date >= starts_from)
    if starts_to:
        stmt = stmt.where(TravelItinerary.start_date <= starts_to)
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    itineraries = db.scalars(
        stmt.order_by(TravelItinerary.start_date.asc(), TravelItinerary.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size),
    ).unique().all()
    return ItineraryList(
        items=[summary(itinerary) for itinerary in itineraries],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, ceil(total / page_size)),
    )


def delete_itinerary(db: Session, user, itinerary_id: str) -> None:
    itinerary = owned_itinerary(db, user, itinerary_id)
    db.delete(itinerary)
    db.commit()


def save_day(db: Session, user, itinerary_id: str, payload: ItineraryDayCreate | ItineraryDayUpdate, day_id: str | None = None) -> ItineraryDetail:
    itinerary = owned_itinerary(db, user, itinerary_id)
    ensure_day_within_trip(itinerary, payload.day_date)
    duplicate = db.scalar(
        select(TravelItineraryDay).where(
            TravelItineraryDay.itinerary_id == itinerary.id,
            TravelItineraryDay.day_date == payload.day_date,
            TravelItineraryDay.id != (day_id or ""),
        ),
    )
    if duplicate:
        fail(409, "An itinerary day already exists for this date.")
    day = owned_day(db, user, itinerary_id, day_id) if day_id else TravelItineraryDay(itinerary_id=itinerary.id)
    for key, value in payload.model_dump().items():
        setattr(day, key, value)
    if not day_id:
        db.add(day)
    db.commit()
    return get_itinerary(db, user, itinerary_id)


def delete_day(db: Session, user, itinerary_id: str, day_id: str) -> None:
    day = owned_day(db, user, itinerary_id, day_id)
    db.delete(day)
    db.commit()


def save_activity(
    db: Session,
    user,
    itinerary_id: str,
    day_id: str,
    payload: ActivityCreate | ActivityUpdate,
    activity_id: str | None = None,
) -> ItineraryDetail:
    day = owned_day(db, user, itinerary_id, day_id)
    category_for(db, user, payload.category_id)
    duplicate = db.scalar(
        select(TravelActivity).where(
            TravelActivity.day_id == day.id,
            func.lower(TravelActivity.title) == payload.title.lower(),
            TravelActivity.start_time == payload.start_time,
            TravelActivity.id != (activity_id or ""),
        ),
    )
    if duplicate:
        fail(409, "An activity with this title and start time already exists on this day.")
    activity = (
        owned_activity(db, user, itinerary_id, day_id, activity_id)
        if activity_id
        else TravelActivity(day_id=day.id)
    )
    for key, value in payload.model_dump().items():
        setattr(activity, key, value)
    if not activity_id:
        db.add(activity)
    db.commit()
    return get_itinerary(db, user, itinerary_id)


def delete_activity(db: Session, user, itinerary_id: str, day_id: str, activity_id: str) -> ItineraryDetail:
    activity = owned_activity(db, user, itinerary_id, day_id, activity_id)
    db.delete(activity)
    db.commit()
    return get_itinerary(db, user, itinerary_id)


def save_category(
    db: Session,
    user,
    payload: TravelCategoryCreate | TravelCategoryUpdate,
    category_id: str | None = None,
) -> TravelCategoryResponse:
    category = owned_category(db, user, category_id) if category_id else TravelActivityCategory(user_id=user_id(user))
    duplicate = db.scalar(
        select(TravelActivityCategory).where(
            TravelActivityCategory.user_id == user_id(user),
            func.lower(TravelActivityCategory.name) == payload.name.lower(),
            TravelActivityCategory.id != (category_id or ""),
        ),
    )
    if duplicate:
        fail(409, "Category name already exists.")
    for key, value in payload.model_dump().items():
        setattr(category, key, value)
    if not category_id:
        db.add(category)
    db.commit()
    db.refresh(category)
    return category_response(db, category)


def list_categories(db: Session, user, q: str | None = None, page: int = 1, page_size: int = 50) -> TravelCategoryList:
    stmt = select(TravelActivityCategory).where(TravelActivityCategory.user_id == user_id(user))
    term = (q or "").strip()
    if term:
        stmt = stmt.where(TravelActivityCategory.name.ilike(f"%{term}%"))
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    categories = db.scalars(
        stmt.order_by(TravelActivityCategory.sort_order, TravelActivityCategory.name)
        .offset((page - 1) * page_size)
        .limit(page_size),
    ).all()
    return TravelCategoryList(
        items=[category_response(db, category) for category in categories],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, ceil(total / page_size)),
    )


def delete_category(db: Session, user, category_id: str) -> None:
    category = owned_category(db, user, category_id)
    count = db.scalar(
        select(func.count()).select_from(TravelActivity).where(TravelActivity.category_id == category_id),
    ) or 0
    if count:
        fail(409, "Move or delete activities before deleting this category.")
    db.delete(category)
    db.commit()


def dashboard(db: Session, user) -> TravelDashboard:
    itineraries = db.scalars(
        select(TravelItinerary)
        .where(TravelItinerary.user_id == user_id(user))
        .options(selectinload(TravelItinerary.days).selectinload(TravelItineraryDay.activities))
        .order_by(TravelItinerary.updated_at.desc()),
    ).unique().all()
    counts = {status: sum(itinerary.status == status for itinerary in itineraries) for status in ["draft", "planned", "active", "completed", "cancelled"]}
    return TravelDashboard(
        **counts,
        upcoming=sum(itinerary.start_date >= date.today() and itinerary.status in {"draft", "planned"} for itinerary in itineraries),
        total_itineraries=len(itineraries),
        total_days=sum(len(itinerary.days) for itinerary in itineraries),
        total_activities=sum(len(day.activities) for itinerary in itineraries for day in itinerary.days),
        recent=[summary(itinerary) for itinerary in itineraries[:5]],
    )

