from datetime import UTC, datetime
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.creative_title_generator import repository
from app.modules.creative_title_generator.models import GeneratedTitle, TitleJob, TitleProject
from app.modules.creative_title_generator.schemas import (
    CreativeTitleGeneratorDashboardResponse,
    GeneratedTitleDetailResponse,
    GeneratedTitleSummaryResponse,
    TitleGenerateRequest,
    TitleGenerationResponse,
    TitleJobResponse,
    TitleProjectCreateRequest,
    TitleProjectDetailResponse,
    TitleProjectSummaryResponse,
    TitleProjectUpdateRequest,
)

PREVIEW_LENGTH = 220


def _preview(value: str) -> str:
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> TitleProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Title project was not found.")
    return project


def _get_owned_generated_title(db: Session, user: User, generated_title_id: int) -> GeneratedTitle:
    generated_title = repository.get_generated_title(db, generated_title_id)
    if not generated_title or generated_title.owner_id != user.id:
        _not_found("Generated title was not found.")
    return generated_title


def _project_summary_response(db: Session, project: TitleProject) -> TitleProjectSummaryResponse:
    latest = repository.latest_generated_title(db, project.id)
    return TitleProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        topic_preview=_preview(project.topic),
        audience=project.audience,
        language=project.language,
        status=project.status,
        generated_count=repository.count_results(db, project.id),
        latest_category=latest.category if latest else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: TitleProject) -> TitleProjectDetailResponse:
    item = _project_summary_response(db, project)
    return TitleProjectDetailResponse(**item.model_dump(), topic=project.topic)


def _generated_title_summary_response(generated_title: GeneratedTitle, project: TitleProject) -> GeneratedTitleSummaryResponse:
    return GeneratedTitleSummaryResponse(
        id=generated_title.id,
        project_id=generated_title.project_id,
        project_title=project.title,
        generated_title=generated_title.generated_title,
        category=generated_title.category,
        score=generated_title.score,
        created_at=generated_title.created_at,
    )


def _generated_title_detail_response(generated_title: GeneratedTitle, project: TitleProject) -> GeneratedTitleDetailResponse:
    item = _generated_title_summary_response(generated_title, project)
    return GeneratedTitleDetailResponse(
        **item.model_dump(),
        topic=project.topic,
        audience=project.audience,
        language=project.language,
    )


def _job_response(job: TitleJob, project: TitleProject) -> TitleJobResponse:
    return TitleJobResponse(
        id=job.id,
        project_id=job.project_id,
        project_title=project.title,
        status=job.status,
        provider=job.provider,
        generation_type=job.generation_type,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


def _clean_phrase(value: str) -> str:
    text = re.sub(r"\s+", " ", value.strip())
    return text[:1].upper() + text[1:] if text else text


def _keyword_suffix(keywords: str | None) -> str:
    if not keywords:
        return ""
    first_keyword = keywords.split(",")[0].strip()
    return f" for {first_keyword}" if first_keyword else ""


def _title_options(project: TitleProject, payload: TitleGenerateRequest) -> list[tuple[str, str, int]]:
    topic = _clean_phrase(project.topic).rstrip(".!?")
    audience = _clean_phrase(project.audience or "readers")
    suffix = _keyword_suffix(payload.keywords)
    style_words = {
        "clear": ("Simple", "Practical"),
        "playful": ("Fresh", "Unexpected"),
        "professional": ("Strategic", "Essential"),
        "bold": ("Powerful", "Breakthrough"),
        "seo": ("Best", "Complete"),
    }
    lead, second = style_words.get(payload.style, ("Creative", "Useful"))
    type_templates = {
        "blog": [
            (f"{lead} Ways to Understand {topic}{suffix}", "Blog", 88),
            (f"{second} Guide to {topic} for {audience}", "Guide", 84),
            (f"What {audience} Should Know About {topic}", "Explainer", 82),
        ],
        "video": [
            (f"{lead} {topic} Ideas That Hook Viewers", "Video", 87),
            (f"{second} {topic}: A Fast Story for {audience}", "Video", 83),
            (f"Why {topic} Matters Now", "Short-form", 81),
        ],
        "product": [
            (f"{lead} {topic} Built for {audience}", "Product", 86),
            (f"{second} Solution for {topic}{suffix}", "Product", 84),
            (f"Make {topic} Easier for {audience}", "Benefit", 82),
        ],
        "social": [
            (f"{lead} Take on {topic}{suffix}", "Social", 85),
            (f"{topic}: The {second} Angle", "Social", 83),
            (f"For {audience}: {topic} in One Line", "Caption", 80),
        ],
        "email": [
            (f"{lead} Update: {topic}", "Email", 86),
            (f"{second} Ideas for {audience}", "Email", 82),
            (f"A Better Way to Think About {topic}", "Newsletter", 81),
        ],
    }
    return type_templates[payload.generation_type]


def list_projects(db: Session, user: User) -> list[TitleProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: TitleProjectCreateRequest) -> TitleProjectDetailResponse:
    project = TitleProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> TitleProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: TitleProjectUpdateRequest) -> TitleProjectDetailResponse:
    project = _get_owned_project(db, user, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def delete_project(db: Session, user: User, project_id: int) -> None:
    project = _get_owned_project(db, user, project_id)
    repository.delete_record(db, project)
    db.commit()


def generate_titles(db: Session, user: User, project_id: int, payload: TitleGenerateRequest) -> TitleGenerationResponse:
    project = _get_owned_project(db, user, project_id)
    generated_titles = [
        GeneratedTitle(
            owner_id=user.id,
            platform_id=project.platform_id,
            project_id=project.id,
            generated_title=title,
            category=category,
            score=score,
        )
        for title, category, score in _title_options(project, payload)
    ]
    job = TitleJob(
        owner_id=user.id,
        platform_id=project.platform_id,
        project_id=project.id,
        status="completed",
        provider="placeholder",
        generation_type=payload.generation_type,
        completed_at=datetime.now(UTC),
    )
    project.status = "active"
    for generated_title in generated_titles:
        repository.add(db, generated_title)
    repository.add(db, job)
    db.commit()
    db.refresh(project)
    for generated_title in generated_titles:
        db.refresh(generated_title)
    db.refresh(job)
    return TitleGenerationResponse(
        project=_project_detail_response(db, project),
        generated_titles=[
            _generated_title_summary_response(generated_title, project)
            for generated_title in generated_titles
        ],
        job=_job_response(job, project),
    )


def list_generated_titles(db: Session, user: User) -> list[GeneratedTitleSummaryResponse]:
    return [
        _generated_title_summary_response(generated_title, project)
        for generated_title, project in repository.list_generated_titles(db, user.id)
    ]


def get_generated_title(db: Session, user: User, generated_title_id: int) -> GeneratedTitleDetailResponse:
    generated_title = _get_owned_generated_title(db, user, generated_title_id)
    project = _get_owned_project(db, user, generated_title.project_id)
    return _generated_title_detail_response(generated_title, project)


def list_history(db: Session, user: User) -> list[TitleJobResponse]:
    return [_job_response(job, project) for job, project in repository.list_history(db, user.id)]


def get_dashboard(db: Session, user: User) -> CreativeTitleGeneratorDashboardResponse:
    projects = list_projects(db, user)
    generated_titles = list_generated_titles(db, user)
    history = list_history(db, user)
    return CreativeTitleGeneratorDashboardResponse(
        projects=projects,
        generated_titles=generated_titles,
        history=history,
        project_count=len(projects),
        generated_count=len(generated_titles),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
    )
