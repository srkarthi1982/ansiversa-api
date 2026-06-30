from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.prompt_builder import repository
from app.modules.prompt_builder.models import Prompt, PromptHistory, PromptProject, PromptTemplate
from app.modules.prompt_builder.schemas import (
    PromptBuilderDashboardResponse,
    PromptCreateRequest,
    PromptDetailResponse,
    PromptHistoryCreateRequest,
    PromptHistoryDetailResponse,
    PromptHistorySummaryResponse,
    PromptHistoryUpdateRequest,
    PromptProjectCreateRequest,
    PromptProjectDetailResponse,
    PromptProjectSummaryResponse,
    PromptProjectUpdateRequest,
    PromptSummaryResponse,
    PromptTemplateCreateRequest,
    PromptTemplateDetailResponse,
    PromptTemplateSummaryResponse,
    PromptTemplateUpdateRequest,
    PromptUpdateRequest,
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


def _get_owned_project(db: Session, user: User, project_id: int) -> PromptProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Prompt project was not found.")
    return project


def _get_owned_prompt(db: Session, user: User, prompt_id: int) -> Prompt:
    prompt = repository.get_prompt(db, prompt_id)
    if not prompt or prompt.owner_id != user.id:
        _not_found("Prompt was not found.")
    return prompt


def _get_owned_template(db: Session, user: User, template_id: int) -> PromptTemplate:
    template = repository.get_template(db, template_id)
    if not template or template.owner_id != user.id:
        _not_found("Prompt template was not found.")
    return template


def _get_owned_history(db: Session, user: User, history_id: int) -> PromptHistory:
    history = repository.get_history(db, history_id)
    if not history or history.owner_id != user.id:
        _not_found("Prompt history record was not found.")
    return history


def _project_summary_response(db: Session, project: PromptProject) -> PromptProjectSummaryResponse:
    return PromptProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        category=project.category,
        status=project.status,
        goal_preview=_preview(project.goal),
        prompt_count=repository.count_prompts(db, project.id),
        template_count=repository.count_templates(db, project.id),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: PromptProject) -> PromptProjectDetailResponse:
    item = _project_summary_response(db, project)
    return PromptProjectDetailResponse(
        **item.model_dump(),
        goal=project.goal,
        notes=project.notes,
    )


def _prompt_summary_response(db: Session, prompt: Prompt, project_title: str) -> PromptSummaryResponse:
    return PromptSummaryResponse(
        id=prompt.id,
        platform_id=prompt.platform_id,
        project_id=prompt.project_id,
        project_title=project_title,
        title=prompt.title,
        category=prompt.category,
        model_target=prompt.model_target,
        status=prompt.status,
        prompt_preview=_preview(prompt.prompt_text),
        context_preview=_preview(prompt.context_text),
        history_count=repository.count_history(db, prompt.id),
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
    )


def _prompt_detail_response(db: Session, prompt: Prompt, project_title: str) -> PromptDetailResponse:
    item = _prompt_summary_response(db, prompt, project_title)
    return PromptDetailResponse(
        **item.model_dump(),
        prompt_text=prompt.prompt_text,
        context_text=prompt.context_text,
        output_format=prompt.output_format,
        tags=prompt.tags,
    )


def _template_summary_response(template: PromptTemplate, project_title: str) -> PromptTemplateSummaryResponse:
    return PromptTemplateSummaryResponse(
        id=template.id,
        platform_id=template.platform_id,
        project_id=template.project_id,
        project_title=project_title,
        title=template.title,
        category=template.category,
        template_preview=_preview(template.template_text),
        usage_notes_preview=_preview(template.usage_notes),
        created_at=template.created_at,
        updated_at=template.updated_at,
    )


def _template_detail_response(template: PromptTemplate, project_title: str) -> PromptTemplateDetailResponse:
    item = _template_summary_response(template, project_title)
    return PromptTemplateDetailResponse(
        **item.model_dump(),
        template_text=template.template_text,
        usage_notes=template.usage_notes,
    )


def _history_summary_response(history: PromptHistory, prompt_title: str) -> PromptHistorySummaryResponse:
    return PromptHistorySummaryResponse(
        id=history.id,
        platform_id=history.platform_id,
        prompt_id=history.prompt_id,
        prompt_title=prompt_title,
        title=history.title,
        event_type=history.event_type,
        occurred_at=history.occurred_at,
        description_preview=_preview(history.description),
        revision_notes_preview=_preview(history.revision_notes),
        created_at=history.created_at,
        updated_at=history.updated_at,
    )


def _history_detail_response(history: PromptHistory, prompt_title: str) -> PromptHistoryDetailResponse:
    item = _history_summary_response(history, prompt_title)
    return PromptHistoryDetailResponse(
        **item.model_dump(),
        description=history.description,
        revision_notes=history.revision_notes,
    )


def list_projects(db: Session, user: User) -> list[PromptProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: PromptProjectCreateRequest) -> PromptProjectDetailResponse:
    project = PromptProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> PromptProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: PromptProjectUpdateRequest) -> PromptProjectDetailResponse:
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


def list_prompts(db: Session, user: User) -> list[PromptSummaryResponse]:
    return [
        _prompt_summary_response(db, prompt, project.title)
        for prompt, project in repository.list_prompts(db, user.id)
    ]


def create_prompt(db: Session, user: User, payload: PromptCreateRequest) -> PromptDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    prompt = Prompt(owner_id=user.id, **payload.model_dump())
    repository.add(db, prompt)
    db.commit()
    db.refresh(prompt)
    return _prompt_detail_response(db, prompt, project.title)


def get_prompt(db: Session, user: User, prompt_id: int) -> PromptDetailResponse:
    prompt = _get_owned_prompt(db, user, prompt_id)
    project = _get_owned_project(db, user, prompt.project_id)
    return _prompt_detail_response(db, prompt, project.title)


def update_prompt(db: Session, user: User, prompt_id: int, payload: PromptUpdateRequest) -> PromptDetailResponse:
    prompt = _get_owned_prompt(db, user, prompt_id)
    project = _get_owned_project(db, user, prompt.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prompt, field, value)
    db.commit()
    db.refresh(prompt)
    return _prompt_detail_response(db, prompt, project.title)


def delete_prompt(db: Session, user: User, prompt_id: int) -> None:
    prompt = _get_owned_prompt(db, user, prompt_id)
    repository.delete_prompt_children(db, prompt.id)
    repository.delete_record(db, prompt)
    db.commit()


def list_templates(db: Session, user: User) -> list[PromptTemplateSummaryResponse]:
    return [
        _template_summary_response(template, project.title)
        for template, project in repository.list_templates(db, user.id)
    ]


def create_template(db: Session, user: User, payload: PromptTemplateCreateRequest) -> PromptTemplateDetailResponse:
    project = _get_owned_project(db, user, payload.project_id)
    template = PromptTemplate(owner_id=user.id, **payload.model_dump())
    repository.add(db, template)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def get_template(db: Session, user: User, template_id: int) -> PromptTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    return _template_detail_response(template, project.title)


def update_template(db: Session, user: User, template_id: int, payload: PromptTemplateUpdateRequest) -> PromptTemplateDetailResponse:
    template = _get_owned_template(db, user, template_id)
    project = _get_owned_project(db, user, template.project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return _template_detail_response(template, project.title)


def delete_template(db: Session, user: User, template_id: int) -> None:
    template = _get_owned_template(db, user, template_id)
    repository.delete_record(db, template)
    db.commit()


def list_history(db: Session, user: User) -> list[PromptHistorySummaryResponse]:
    return [
        _history_summary_response(history, prompt.title)
        for history, prompt in repository.list_history(db, user.id)
    ]


def create_history(db: Session, user: User, payload: PromptHistoryCreateRequest) -> PromptHistoryDetailResponse:
    prompt = _get_owned_prompt(db, user, payload.prompt_id)
    history = PromptHistory(owner_id=user.id, **payload.model_dump())
    repository.add(db, history)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, prompt.title)


def get_history(db: Session, user: User, history_id: int) -> PromptHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    prompt = _get_owned_prompt(db, user, history.prompt_id)
    return _history_detail_response(history, prompt.title)


def update_history(db: Session, user: User, history_id: int, payload: PromptHistoryUpdateRequest) -> PromptHistoryDetailResponse:
    history = _get_owned_history(db, user, history_id)
    prompt = _get_owned_prompt(db, user, history.prompt_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(history, field, value)
    db.commit()
    db.refresh(history)
    return _history_detail_response(history, prompt.title)


def delete_history(db: Session, user: User, history_id: int) -> None:
    history = _get_owned_history(db, user, history_id)
    repository.delete_record(db, history)
    db.commit()


def get_dashboard(db: Session, user: User) -> PromptBuilderDashboardResponse:
    projects = list_projects(db, user)
    prompts = list_prompts(db, user)
    templates = list_templates(db, user)
    history = list_history(db, user)
    return PromptBuilderDashboardResponse(
        projects=projects,
        prompts=prompts,
        templates=templates,
        history=history,
        project_count=len(projects),
        prompt_count=len(prompts),
        template_count=len(templates),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
        ready_prompt_count=sum(1 for item in prompts if item.status == "ready"),
    )
