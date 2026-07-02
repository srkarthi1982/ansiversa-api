from datetime import UTC, datetime
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.grammar_and_paraphrasing_assistant import repository
from app.modules.grammar_and_paraphrasing_assistant.models import GrammarJob, GrammarProject, GrammarResult
from app.modules.grammar_and_paraphrasing_assistant.schemas import (
    GrammarAndParaphrasingDashboardResponse,
    GrammarJobResponse,
    GrammarProjectCreateRequest,
    GrammarProjectDetailResponse,
    GrammarProjectSummaryResponse,
    GrammarProjectUpdateRequest,
    GrammarResultDetailResponse,
    GrammarResultSummaryResponse,
    GrammarRunRequest,
    GrammarRunResponse,
)

PREVIEW_LENGTH = 220


def _preview(value: str) -> str:
    if len(value) <= PREVIEW_LENGTH:
        return value
    return f"{value[:PREVIEW_LENGTH].rstrip()}..."


def _not_found(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _get_owned_project(db: Session, user: User, project_id: int) -> GrammarProject:
    project = repository.get_project(db, project_id)
    if not project or project.owner_id != user.id:
        _not_found("Grammar project was not found.")
    return project


def _get_owned_result(db: Session, user: User, result_id: int) -> GrammarResult:
    result = repository.get_result(db, result_id)
    if not result or result.owner_id != user.id:
        _not_found("Grammar result was not found.")
    return result


def _project_summary_response(db: Session, project: GrammarProject) -> GrammarProjectSummaryResponse:
    latest = repository.latest_result(db, project.id)
    return GrammarProjectSummaryResponse(
        id=project.id,
        platform_id=project.platform_id,
        title=project.title,
        language=project.language,
        status=project.status,
        original_preview=_preview(project.original_text),
        result_count=repository.count_results(db, project.id),
        latest_tone=latest.tone if latest else None,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _project_detail_response(db: Session, project: GrammarProject) -> GrammarProjectDetailResponse:
    item = _project_summary_response(db, project)
    return GrammarProjectDetailResponse(**item.model_dump(), original_text=project.original_text)


def _result_summary_response(result: GrammarResult, project: GrammarProject) -> GrammarResultSummaryResponse:
    return GrammarResultSummaryResponse(
        id=result.id,
        project_id=result.project_id,
        project_title=project.title,
        corrected_preview=_preview(result.corrected_text),
        paraphrased_preview=_preview(result.paraphrased_text),
        tone=result.tone,
        grammar_score=result.grammar_score,
        readability_score=result.readability_score,
        created_at=result.created_at,
    )


def _result_detail_response(result: GrammarResult, project: GrammarProject) -> GrammarResultDetailResponse:
    item = _result_summary_response(result, project)
    return GrammarResultDetailResponse(
        **item.model_dump(),
        original_text=project.original_text,
        corrected_text=result.corrected_text,
        paraphrased_text=result.paraphrased_text,
    )


def _job_response(job: GrammarJob, project: GrammarProject) -> GrammarJobResponse:
    return GrammarJobResponse(
        id=job.id,
        project_id=job.project_id,
        project_title=project.title,
        status=job.status,
        provider=job.provider,
        action=job.action,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


def _correct_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value.strip())
    if not text:
        return text
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def _paraphrase_text(value: str, tone: str) -> str:
    corrected = _correct_text(value)
    prefixes = {
        "professional": "Professional version:",
        "friendly": "Friendly version:",
        "concise": "Concise version:",
        "confident": "Confident version:",
        "clear": "Clear version:",
    }
    return f"{prefixes.get(tone, 'Clear version:')} {corrected}"


def _score_text(value: str) -> tuple[int, int]:
    word_count = len(value.split())
    grammar_score = max(65, min(96, 78 + min(word_count, 18)))
    readability_score = max(60, min(94, 82 - max(0, word_count - 40) // 5))
    return grammar_score, readability_score


def list_projects(db: Session, user: User) -> list[GrammarProjectSummaryResponse]:
    return [_project_summary_response(db, project) for project in repository.list_projects(db, user.id)]


def create_project(db: Session, user: User, payload: GrammarProjectCreateRequest) -> GrammarProjectDetailResponse:
    project = GrammarProject(owner_id=user.id, **payload.model_dump())
    repository.add(db, project)
    db.commit()
    db.refresh(project)
    return _project_detail_response(db, project)


def get_project(db: Session, user: User, project_id: int) -> GrammarProjectDetailResponse:
    return _project_detail_response(db, _get_owned_project(db, user, project_id))


def update_project(db: Session, user: User, project_id: int, payload: GrammarProjectUpdateRequest) -> GrammarProjectDetailResponse:
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


def run_project(db: Session, user: User, project_id: int, payload: GrammarRunRequest) -> GrammarRunResponse:
    project = _get_owned_project(db, user, project_id)
    corrected = _correct_text(project.original_text)
    paraphrased = _paraphrase_text(project.original_text, payload.tone)
    grammar_score, readability_score = _score_text(corrected)
    result = GrammarResult(
        owner_id=user.id,
        platform_id=project.platform_id,
        project_id=project.id,
        corrected_text=corrected,
        paraphrased_text=paraphrased,
        tone=payload.tone,
        grammar_score=grammar_score,
        readability_score=readability_score,
    )
    job = GrammarJob(
        owner_id=user.id,
        platform_id=project.platform_id,
        project_id=project.id,
        status="completed",
        provider="placeholder",
        action=payload.action,
        completed_at=datetime.now(UTC),
    )
    project.status = "active"
    repository.add(db, result)
    repository.add(db, job)
    db.commit()
    db.refresh(project)
    db.refresh(result)
    db.refresh(job)
    return GrammarRunResponse(
        project=_project_detail_response(db, project),
        result=_result_detail_response(result, project),
        job=_job_response(job, project),
    )


def list_results(db: Session, user: User) -> list[GrammarResultSummaryResponse]:
    return [_result_summary_response(result, project) for result, project in repository.list_results(db, user.id)]


def get_result(db: Session, user: User, result_id: int) -> GrammarResultDetailResponse:
    result = _get_owned_result(db, user, result_id)
    project = _get_owned_project(db, user, result.project_id)
    return _result_detail_response(result, project)


def list_history(db: Session, user: User) -> list[GrammarJobResponse]:
    return [_job_response(job, project) for job, project in repository.list_history(db, user.id)]


def get_dashboard(db: Session, user: User) -> GrammarAndParaphrasingDashboardResponse:
    projects = list_projects(db, user)
    results = list_results(db, user)
    history = list_history(db, user)
    return GrammarAndParaphrasingDashboardResponse(
        projects=projects,
        results=results,
        history=history,
        project_count=len(projects),
        result_count=len(results),
        history_count=len(history),
        active_project_count=sum(1 for item in projects if item.status == "active"),
    )
