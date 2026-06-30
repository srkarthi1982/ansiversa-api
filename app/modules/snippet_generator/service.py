from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.snippet_generator import repository
from app.modules.snippet_generator.models import Snippet, SnippetCategory, SnippetHistory, SnippetProject
from app.modules.snippet_generator.schemas import (
    SnippetCategoryCreateRequest,
    SnippetCategoryDetailResponse,
    SnippetCategorySummaryResponse,
    SnippetCategoryUpdateRequest,
    SnippetCreateRequest,
    SnippetDetailResponse,
    SnippetGeneratorDashboardResponse,
    SnippetHistoryCreateRequest,
    SnippetHistoryDetailResponse,
    SnippetHistorySummaryResponse,
    SnippetHistoryUpdateRequest,
    SnippetProjectCreateRequest,
    SnippetProjectDetailResponse,
    SnippetProjectSummaryResponse,
    SnippetProjectUpdateRequest,
    SnippetSummaryResponse,
    SnippetUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> SnippetProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Snippet project was not found.")
    return project


def _get_owned_snippet(db: Session, user: User, snippet_id: int) -> Snippet:
    snippet = repository.get_snippet(db, snippet_id)
    if not snippet or snippet.owner_id != user.id:
        _not_found("Snippet was not found.")
    return snippet


def _get_owned_category(db: Session, user: User, category_id: int) -> SnippetCategory:
    category = repository.get_category(db, category_id)
    if not category or category.owner_id != user.id:
        _not_found("Snippet category was not found.")
    return category


def _get_owned_history(db: Session, user: User, history_id: int) -> SnippetHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Snippet history record was not found.")
    return history


def _project_summary_response(db: Session, project: SnippetProject) -> SnippetProjectSummaryResponse:
    return SnippetProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        language=project.language,
        status=project.status,
        goal_preview=_preview(project.goal),
        snippet_count=repository.count_snippets(db, project.id),
        category_count=repository.count_categories(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: SnippetProject) -> SnippetProjectDetailResponse:
    item = _project_summary_response(db, project)
    return SnippetProjectDetailResponse(
        **item.model_dump(),
        goal=project.goal,
        notes=project.notes,
    )


def _category_summary_response(db: Session, category: SnippetCategory, project_title: str) -> SnippetCategorySummaryResponse:
    return SnippetCategorySummaryResponse(
        id=category.id,
        platform_id=category.platform_id,
        project_id=category.project_id,
        project_title=project_title,
        name=category.name,
        color=category.color,
        description_preview=_preview(category.description),
        snippet_count=repository.count_category_snippets(db, category.id),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _category_detail_response(db: Session, category: SnippetCategory, project_title: str) -> SnippetCategoryDetailResponse:
    item = _category_summary_response(db, category, project_title)
    return SnippetCategoryDetailResponse(
        **item.model_dump(),
        description=category.description,
    )


def _snippet_summary_response(db: Session, snippet: Snippet, project_title: str, category_name: str | None) -> SnippetSummaryResponse:
    return SnippetSummaryResponse(
        id=snippet.id,
        platform_id=snippet.platform_id,
        project_id=snippet.project_id,
        project_title=project_title,
        category_id=snippet.category_id,
        category_name=category_name,
        title=snippet.title,
        language=snippet.language,
        status=snippet.status,
        description_preview=_preview(snippet.description),
        snippet_preview=_preview(snippet.snippet_text),
        history_count=repository.count_history(db, snippet.id),
        created_at=snippet.created_at,
        updated_at=snippet.updated_at,
    )


def _snippet_detail_response(db: Session, snippet: Snippet, project_title: str, category_name: str | None) -> SnippetDetailResponse:
    item = _snippet_summary_response(db, snippet, project_title, category_name)
    return SnippetDetailResponse(
        **item.model_dump(),
        description=snippet.description,
        snippet_text=snippet.snippet_text,
        usage_notes=snippet.usage_notes,
        tags=snippet.tags,
    )


def _history_summary_response(history: SnippetHistory, snippet_title: str) -> SnippetHistorySummaryResponse:
    return SnippetHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        snippet_id=history.snippet_id,
        snippet_title=snippet_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: SnippetHistory, snippet_title: str) -> SnippetHistoryDetailResponse:
    item = _history_summary_response(history, snippet_title)
    return SnippetHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_projects(db: Session, user: User) -> list[SnippetProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: SnippetProjectCreateRequest) -> SnippetProjectDetailResponse:
    project = SnippetProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> SnippetProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: SnippetProjectUpdateRequest) -> SnippetProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    repository.delete_project_children(db, project.id)
    repository.delete_record(db, project)
    db.commit()


def list_categories(db: Session, user: User) -> list[SnippetCategorySummaryResponse]:
    return [
        _category_summary_response(db, category, project.title)
        for category, project in repository.list_categories(db, user.id)
    ]


def create_category(db: Session, user: User, payload: SnippetCategoryCreateRequest) -> SnippetCategoryDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    category = SnippetCategory(owner_id=user.id, **payload.model_dump())
    repository.add(db, category)
    db.commit()
    db.refresh(category)
    return _category_detail_response(db, category, project.title)


def get_category(db: Session, user: User, category_id: int) -> SnippetCategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    project = _get_owned_project(db, user, category.project_id)
    return _category_detail_response(db, category, project.title)


def update_category(db: Session, user: User, category_id: int, payload: SnippetCategoryUpdateRequest) -> SnippetCategoryDetailResponse:
    category = _get_owned_category(db, user, category_id)
    project = _get_owned_project(db, user, category.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return _category_detail_response(db, category, project.title)


def delete_category(db: Session, user: User, category_id: int) -> None:
    category = _get_owned_category(db, user, category_id)
    repository.clear_category_from_snippets(db, category.id)
    repository.delete_record(db, category)
    db.commit()


def list_snippets(db: Session, user: User) -> list[SnippetSummaryResponse]:
    return [
        _snippet_summary_response(db, snippet, project.title, category.name if category else None)
        for snippet, project, category in repository.list_snippets(db, user.id)
    ]


def create_snippet(db: Session, user: User, payload: SnippetCreateRequest) -> SnippetDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    category = None
    if payload.category_id is not None:
        category = _get_owned_category(db, user, payload.category_id)
        if category.project_id != project.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Snippet category does not belong to the selected project.")
    snippet = Snippet(owner_id=user.id, **payload.model_dump())
    repository.add(db, snippet)
    db.commit()
    db.refresh(snippet)
    return _snippet_detail_response(db, snippet, project.title, category.name if category else None)


def get_snippet(db: Session, user: User, snippet_id: int) -> SnippetDetailResponse:
    snippet = _get_owned_snippet(db, user, snippet_id)
    project = _get_owned_project(db, user, snippet.project_id)
    category = repository.get_category(db, snippet.category_id) if snippet.category_id else None
    return _snippet_detail_response(db, snippet, project.title, category.name if category else None)


def update_snippet(db: Session, user: User, snippet_id: int, payload: SnippetUpdateRequest) -> SnippetDetailResponse:
    snippet = _get_owned_snippet(db, user, snippet_id)
    project = _get_owned_project(db, user, snippet.project_id)
    category = repository.get_category(db, snippet.category_id) if snippet.category_id else None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(snippet, field, value)
    db.commit()
    db.refresh(snippet)
    return _snippet_detail_response(db, snippet, project.title, category.name if category else None)


def delete_snippet(db: Session, user: User, snippet_id: int) -> None:
    snippet = _get_owned_snippet(db, user, snippet_id)
    repository.delete_snippet_children(db, snippet.id)
    repository.delete_record(db, snippet)
    db.commit()


def list_history(db: Session, user: User) -> list[SnippetHistorySummaryResponse]:
    return [
        _history_summary_response(history, snippet.title)
        for history, snippet in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: SnippetHistoryCreateRequest) -> SnippetHistoryDetailResponse:
    snippet = _get_owned_snippet(db, user, payload.snippet_id)
    history = SnippetHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, snippet.title)


def get_history(db: Session, user: User, history_id: int) -> SnippetHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    snippet = _get_owned_snippet(db, user, history.snippet_id)
    return _history_detail_response(history, snippet.title)


def update_history(db: Session, user: User, history_id: int, payload: SnippetHistoryUpdateRequest) -> SnippetHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    snippet = _get_owned_snippet(db, user, history.snippet_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, snippet.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> SnippetGeneratorDashboardResponse:
    projects = list_projects(db, user)
    snippets = list_snippets(db, user)
    categories = list_categories(db, user)
    history = list_history(db, user)
    return SnippetGeneratorDashboardResponse(
        projects=projects,
        snippets=snippets,
        categories=categories,
        history=history,
        project_count=len(projects),
        snippet_count=len(snippets),
        category_count=len(categories),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
        ready_snippet_count=sum(1 for item in snippets if item.status == "ready"),
    )
