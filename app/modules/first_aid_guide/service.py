from __future__ import annotations
from collections import Counter
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.modules.first_aid_guide import repository
from app.modules.first_aid_guide.models import FirstAidCategory, FirstAidGuide, UserGuideBookmark, UserGuideHistory
from app.modules.first_aid_guide.schemas import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest, CountItem, DashboardResponse, GuideCreateRequest, GuideDetailResponse, GuideListResponse, GuideSort, GuideSummaryResponse, GuideUpdateRequest, InsightsResponse

DISCLAIMER = "Educational reference only. Contact local emergency services or qualified healthcare professionals when appropriate."
CATEGORIES = [
    ("Cuts and bleeding", "Basic bleeding-control reference.", 10),
    ("Burns", "Educational burn response reference.", 20),
    ("Fractures and sprains", "Immobilization and care awareness.", 30),
    ("Choking", "Emergency awareness for airway obstruction.", 40),
    ("CPR awareness", "CPR learning and professional training awareness.", 50),
    ("Fainting", "Observation and safety positioning reference.", 60),
    ("Heat exhaustion", "Heat illness awareness.", 70),
    ("Heat stroke", "Emergency heat illness warning signs.", 80),
    ("Hypothermia", "Cold exposure awareness.", 90),
    ("Poisoning awareness", "Poison exposure response awareness.", 100),
    ("Allergic reactions", "Allergy warning awareness.", 110),
    ("Insect bites", "Bite and sting reference.", 120),
    ("Animal bites", "Animal bite reference.", 130),
    ("Nosebleeds", "Nosebleed reference.", 140),
    ("Eye injuries", "Eye safety reference.", 150),
    ("Electrical injuries", "Electrical injury emergency awareness.", 160),
    ("Emergency preparedness", "Preparation and prevention tips.", 170),
    ("Other", "General first-aid reference.", 180),
]
GUIDES = [
    ("Cuts and bleeding", "Minor cuts and bleeding", "Clean and protect minor cuts while watching for heavy bleeding.", "For minor cuts, stay calm, wash hands if possible, and protect the area from contamination. " + DISCLAIMER, "Apply gentle pressure with clean material. Rinse minor dirt with clean water. Cover with a clean dressing. Check that bleeding slows.", "Do not use dirty material, remove deeply embedded objects, or delay urgent care for heavy bleeding.", "Seek emergency help for severe bleeding, deep wounds, embedded objects, loss of feeling, or signs of shock.", "Keep a stocked first-aid kit and use protective gloves when available.", "Nosebleeds; Animal bites", 10),
    ("Burns", "Minor burns", "Cool minor burns and avoid harmful home remedies.", "This topic covers small, minor burns only. " + DISCLAIMER, "Cool the burn under cool running water. Remove tight jewelry near the area if easy. Cover loosely with a clean non-stick dressing.", "Do not apply butter, ice directly, or break blisters.", "Seek urgent care for large, deep, chemical, electrical, face, hand, genital, or breathing-related burns.", "Use caution around hot liquids, cooking surfaces, and chemicals.", "Electrical injuries; Heat exhaustion", 20),
    ("Choking", "Choking awareness", "Recognize choking and call emergency services when breathing is blocked.", "Choking can become life-threatening quickly. " + DISCLAIMER, "If the person cannot breathe, cough, or speak, call emergency services. Follow locally approved first-aid training steps if trained.", "Do not perform blind finger sweeps or delay emergency help.", "Seek emergency help immediately for severe choking, unconsciousness, blue lips, or breathing difficulty.", "Cut food appropriately and supervise children while eating.", "CPR awareness", 30),
    ("CPR awareness", "CPR awareness", "Know when CPR training and emergency services matter.", "This guide is awareness only and does not replace certified CPR training. " + DISCLAIMER, "If someone is unresponsive and not breathing normally, call emergency services. Follow dispatcher instructions and use an AED if available and trained.", "Do not wait to call emergency services or practice untrained techniques on a person unnecessarily.", "Call emergency services immediately for unresponsiveness or abnormal breathing.", "Consider certified CPR/AED training from a recognized provider.", "Choking; Electrical injuries", 40),
    ("Heat stroke", "Heat stroke warning signs", "Heat stroke is an emergency and needs urgent help.", "Heat stroke can be life-threatening. " + DISCLAIMER, "Call emergency services. Move the person to a cooler place if safe. Begin cooling with available safe methods while waiting for help.", "Do not give fluids to an unconscious person or delay emergency help.", "Seek emergency help for confusion, collapse, very high temperature, seizures, or hot dry skin.", "Avoid extreme heat exposure and hydrate appropriately.", "Heat exhaustion", 50),
    ("Allergic reactions", "Allergic reaction awareness", "Watch for severe allergy signs and seek urgent care.", "Allergic reactions can range from mild to severe. " + DISCLAIMER, "Move away from the trigger if safe. Observe breathing and swelling. Follow the person's prescribed emergency plan if they have one.", "Do not recommend or share medication. Do not delay emergency help for breathing or swelling symptoms.", "Seek emergency help for trouble breathing, swelling of face or throat, fainting, or rapidly worsening symptoms.", "Know known allergies and avoid triggers where possible.", "Insect bites; Poisoning awareness", 60),
    ("Nosebleeds", "Nosebleeds", "Use simple positioning and pressure for many nosebleeds.", "Most nosebleeds are minor, but some need care. " + DISCLAIMER, "Sit upright and lean slightly forward. Pinch the soft part of the nose. Keep steady pressure for several minutes.", "Do not tilt the head back or pack the nose with unsafe material.", "Seek care for heavy bleeding, injury, breathing trouble, blood-thinner use, or bleeding that does not stop.", "Use humidification and avoid nose picking when relevant.", "Cuts and bleeding", 70),
    ("Emergency preparedness", "First-aid kit basics", "Prepare supplies before they are needed.", "Preparedness supports safer response but does not replace emergency care. " + DISCLAIMER, "Keep clean dressings, gloves, bandages, antiseptic wipes, emergency numbers, and any personally prescribed emergency items available.", "Do not store expired or unlabelled supplies.", "Call emergency services for urgent or life-threatening situations.", "Review supplies periodically and keep emergency contacts current.", "CPR awareness; Cuts and bleeding", 80),
]


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message) from exc


def ensure_seed_data(db: Session) -> None:
    existing = {c.name: c for c in repository.list_categories(db)}
    created = False
    for name, description, order in CATEGORIES:
        if name not in existing:
            repository.add(db, FirstAidCategory(name=name, description=description, sort_order=order, is_system=True))
            created = True
    if created:
        _commit(db, "Unable to prepare first-aid categories.")
        existing = {c.name: c for c in repository.list_categories(db)}
    guide_titles = {g.title for g in repository.list_guides(db)}
    for category_name, title, summary, overview, steps, avoid, warning, prevention, related, order in GUIDES:
        if title not in guide_titles:
            repository.add(db, FirstAidGuide(category_id=existing[category_name].id, title=title, summary=summary, overview=overview, first_aid_steps=steps, avoid_actions=avoid, emergency_warning=warning, prevention=prevention, related_topics=related, display_order=order, last_reviewed=date(2026, 7, 15)))
            created = True
    if created:
        _commit(db, "Unable to prepare first-aid guides.")


def _not_found(name: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} was not found.")


def _guide_or_404(db: Session, guide_id: str) -> FirstAidGuide:
    guide = repository.get_guide(db, guide_id)
    if not guide:
        _not_found("First aid guide")
    return guide


def _category_or_404(db: Session, category_id: str) -> FirstAidCategory:
    category = repository.get_category(db, category_id)
    if not category:
        _not_found("First aid category")
    return category


def _summary(item: FirstAidGuide, bookmarks: set[str], views: dict[str, int]) -> GuideSummaryResponse:
    return GuideSummaryResponse(id=item.id, category_id=item.category_id, category_name=item.category.name, title=item.title, summary=item.summary, emergency_warning=item.emergency_warning, display_order=item.display_order, last_reviewed=item.last_reviewed, is_bookmarked=item.id in bookmarks, view_count=views.get(item.id, 0), created_at=item.created_at, updated_at=item.updated_at)


def _detail(item: FirstAidGuide, bookmarks: set[str], views: dict[str, int]) -> GuideDetailResponse:
    data = _summary(item, bookmarks, views).model_dump()
    return GuideDetailResponse(**data, overview=item.overview, first_aid_steps=item.first_aid_steps, avoid_actions=item.avoid_actions, prevention=item.prevention, related_topics=item.related_topics)


def _category_response(item: FirstAidCategory, counts: dict[str, int]) -> CategoryResponse:
    return CategoryResponse(id=item.id, name=item.name, description=item.description, sort_order=item.sort_order, is_system=item.is_system, guide_count=counts.get(item.id, 0), created_at=item.created_at, updated_at=item.updated_at)


def list_categories(db: Session) -> list[CategoryResponse]:
    ensure_seed_data(db)
    counts = repository.guide_counts_by_category(db)
    return [_category_response(item, counts) for item in repository.list_categories(db)]


def create_category(db: Session, payload: CategoryCreateRequest) -> CategoryResponse:
    item = FirstAidCategory(name=payload.name, description=payload.description, sort_order=payload.sort_order, is_system=False)
    repository.add(db, item)
    _commit(db, "A first-aid category with this name already exists.")
    db.refresh(item)
    return _category_response(item, repository.guide_counts_by_category(db))


def update_category(db: Session, category_id: str, payload: CategoryUpdateRequest) -> CategoryResponse:
    item = _category_or_404(db, category_id)
    item.name = payload.name
    item.description = payload.description
    item.sort_order = payload.sort_order
    _commit(db, "A first-aid category with this name already exists.")
    db.refresh(item)
    return _category_response(item, repository.guide_counts_by_category(db))


def delete_category(db: Session, category_id: str) -> None:
    item = _category_or_404(db, category_id)
    if repository.count_guides_for_category(db, category_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Delete linked guide topics before deleting this category.")
    repository.delete(db, item)
    db.commit()


def _filtered_guides(db: Session, user: User, q: str | None, category_id: str | None, bookmarked: bool, sort_by: GuideSort) -> list[FirstAidGuide]:
    ensure_seed_data(db)
    guides = repository.list_guides(db)
    bookmarks = repository.bookmark_ids(db, user.id)
    views = repository.history_counts(db, user.id)
    if category_id:
        guides = [g for g in guides if g.category_id == category_id]
    if bookmarked:
        guides = [g for g in guides if g.id in bookmarks]
    if q:
        needle = q.lower()
        guides = [g for g in guides if needle in " ".join([g.title, g.summary, g.overview, g.first_aid_steps, g.avoid_actions, g.emergency_warning, g.prevention or "", g.related_topics or "", g.category.name]).lower()]
    if sort_by == "title":
        guides.sort(key=lambda g: g.title)
    elif sort_by == "category":
        guides.sort(key=lambda g: (g.category.sort_order, g.display_order, g.title))
    elif sort_by == "reviewed":
        guides.sort(key=lambda g: (g.last_reviewed or date.min, g.display_order), reverse=True)
    elif sort_by == "viewed":
        guides.sort(key=lambda g: views.get(g.id, 0), reverse=True)
    else:
        guides.sort(key=lambda g: (g.display_order, g.title))
    return guides


def list_guides(db: Session, user: User, q: str | None, category_id: str | None, bookmarked: bool, sort_by: GuideSort, page: int, page_size: int) -> GuideListResponse:
    guides = _filtered_guides(db, user, q, category_id, bookmarked, sort_by)
    bookmarks = repository.bookmark_ids(db, user.id)
    views = repository.history_counts(db, user.id)
    start = (page - 1) * page_size
    return GuideListResponse(items=[_summary(g, bookmarks, views) for g in guides[start:start + page_size]], total=len(guides), page=page, page_size=page_size)


def get_guide(db: Session, user: User, guide_id: str, track_view: bool = True) -> GuideDetailResponse:
    ensure_seed_data(db)
    guide = _guide_or_404(db, guide_id)
    if track_view:
        repository.add(db, UserGuideHistory(owner_id=user.id, guide_id=guide.id))
        db.commit()
    return _detail(guide, repository.bookmark_ids(db, user.id), repository.history_counts(db, user.id))


def create_guide(db: Session, payload: GuideCreateRequest) -> GuideDetailResponse:
    category = _category_or_404(db, payload.category_id)
    item = FirstAidGuide(category_id=category.id, title=payload.title, summary=payload.summary, overview=payload.overview, first_aid_steps=payload.first_aid_steps, avoid_actions=payload.avoid_actions, emergency_warning=payload.emergency_warning, prevention=payload.prevention, related_topics=payload.related_topics, display_order=payload.display_order, last_reviewed=payload.last_reviewed)
    repository.add(db, item)
    _commit(db, "A first-aid guide with this title already exists.")
    return _detail(repository.get_guide(db, item.id), set(), {})


def update_guide(db: Session, guide_id: str, payload: GuideUpdateRequest) -> GuideDetailResponse:
    item = _guide_or_404(db, guide_id)
    category = _category_or_404(db, payload.category_id)
    item.category_id = category.id
    item.title = payload.title
    item.summary = payload.summary
    item.overview = payload.overview
    item.first_aid_steps = payload.first_aid_steps
    item.avoid_actions = payload.avoid_actions
    item.emergency_warning = payload.emergency_warning
    item.prevention = payload.prevention
    item.related_topics = payload.related_topics
    item.display_order = payload.display_order
    item.last_reviewed = payload.last_reviewed
    _commit(db, "A first-aid guide with this title already exists.")
    return _detail(repository.get_guide(db, guide_id), set(), {})


def delete_guide(db: Session, guide_id: str) -> None:
    repository.delete(db, _guide_or_404(db, guide_id))
    db.commit()


def set_bookmark(db: Session, user: User, guide_id: str, bookmarked: bool) -> GuideDetailResponse:
    guide = _guide_or_404(db, guide_id)
    existing = repository.get_bookmark(db, user.id, guide.id)
    if bookmarked and not existing:
        repository.add(db, UserGuideBookmark(owner_id=user.id, guide_id=guide.id))
    if not bookmarked and existing:
        repository.delete(db, existing)
    _commit(db, "Unable to update bookmark.")
    return _detail(guide, repository.bookmark_ids(db, user.id), repository.history_counts(db, user.id))


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    ensure_seed_data(db)
    bookmarks = repository.bookmark_ids(db, user.id)
    recent = repository.recent_history_guide_ids(db, user.id)
    return DashboardResponse(total_guides=len(repository.list_guides(db)), total_categories=len(repository.list_categories(db)), favourite_guides=len(bookmarks), recently_viewed=len(recent), total_history=repository.total_history(db, user.id))


def get_insights(db: Session, user: User) -> InsightsResponse:
    ensure_seed_data(db)
    dashboard = get_dashboard(db, user)
    guides = repository.list_guides(db)
    by_id = {g.id: g for g in guides}
    bookmarks = repository.bookmark_ids(db, user.id)
    views = repository.history_counts(db, user.id)
    recent_ids = repository.recent_history_guide_ids(db, user.id)
    category_counts = Counter(g.category.name for g in guides)
    most_viewed = sorted(guides, key=lambda g: views.get(g.id, 0), reverse=True)[:8]
    return InsightsResponse(**dashboard.model_dump(), categories=list_categories(db), favourite_topics=[_summary(by_id[g], bookmarks, views) for g in bookmarks if g in by_id][:8], recently_viewed_topics=[_summary(by_id[g], bookmarks, views) for g in recent_ids if g in by_id], most_viewed_topics=[_summary(g, bookmarks, views) for g in most_viewed if views.get(g.id, 0) > 0], guides_by_category=[CountItem(label=k, count=v) for k, v in category_counts.most_common()])
