from typing import Annotated

from fastapi import APIRouter, Path, status

from app.modules.job_description_analyzer.dependencies import CurrentUser, JobDescriptionAnalyzerDb
from app.modules.job_description_analyzer.schemas import (
    AnalysisHistoryCreateRequest,
    AnalysisHistoryDetailResponse,
    AnalysisHistorySummaryResponse,
    AnalysisHistoryUpdateRequest,
    JobAnalysisCreateRequest,
    JobAnalysisDetailResponse,
    JobAnalysisSummaryResponse,
    JobAnalysisUpdateRequest,
    JobDescriptionAnalyzerDashboardResponse,
    JobDescriptionCreateRequest,
    JobDescriptionDetailResponse,
    JobDescriptionSummaryResponse,
    JobDescriptionUpdateRequest,
    SkillMatchCreateRequest,
    SkillMatchDetailResponse,
    SkillMatchSummaryResponse,
    SkillMatchUpdateRequest,
)
from app.modules.job_description_analyzer.service import (
    create_analysis,
    create_history,
    create_job,
    create_skill,
    delete_analysis,
    delete_history,
    delete_job,
    delete_skill,
    get_analysis,
    get_dashboard,
    get_history,
    get_job,
    get_skill,
    list_analysis,
    list_history,
    list_jobs,
    list_skills,
    update_analysis,
    update_history,
    update_job,
    update_skill,
)

router = APIRouter()


@router.get("/dashboard", response_model=JobDescriptionAnalyzerDashboardResponse)
def get_job_description_analyzer_dashboard(current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobDescriptionAnalyzerDashboardResponse:
    return get_dashboard(db, current_user)


@router.post("/jobs", response_model=JobDescriptionDetailResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(payload: JobDescriptionCreateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobDescriptionDetailResponse:
    return create_job(db, current_user, payload)


@router.get("/jobs", response_model=list[JobDescriptionSummaryResponse])
def list_job_descriptions(current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> list[JobDescriptionSummaryResponse]:
    return list_jobs(db, current_user)


@router.get("/jobs/{job_id}", response_model=JobDescriptionDetailResponse)
def get_job_description(job_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobDescriptionDetailResponse:
    return get_job(db, current_user, job_id)


@router.put("/jobs/{job_id}", response_model=JobDescriptionDetailResponse)
def update_job_description(job_id: Annotated[int, Path(gt=0)], payload: JobDescriptionUpdateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobDescriptionDetailResponse:
    return update_job(db, current_user, job_id, payload)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_description(job_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> None:
    delete_job(db, current_user, job_id)


@router.post("/analysis", response_model=JobAnalysisDetailResponse, status_code=status.HTTP_201_CREATED)
def create_job_analysis(payload: JobAnalysisCreateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobAnalysisDetailResponse:
    return create_analysis(db, current_user, payload)


@router.get("/analysis", response_model=list[JobAnalysisSummaryResponse])
def list_job_analysis(current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> list[JobAnalysisSummaryResponse]:
    return list_analysis(db, current_user)


@router.get("/analysis/{analysis_id}", response_model=JobAnalysisDetailResponse)
def get_job_analysis(analysis_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobAnalysisDetailResponse:
    return get_analysis(db, current_user, analysis_id)


@router.put("/analysis/{analysis_id}", response_model=JobAnalysisDetailResponse)
def update_job_analysis(analysis_id: Annotated[int, Path(gt=0)], payload: JobAnalysisUpdateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> JobAnalysisDetailResponse:
    return update_analysis(db, current_user, analysis_id, payload)


@router.delete("/analysis/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_analysis(analysis_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> None:
    delete_analysis(db, current_user, analysis_id)


@router.post("/skills", response_model=SkillMatchDetailResponse, status_code=status.HTTP_201_CREATED)
def create_skill_match(payload: SkillMatchCreateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> SkillMatchDetailResponse:
    return create_skill(db, current_user, payload)


@router.get("/skills", response_model=list[SkillMatchSummaryResponse])
def list_skill_matches(current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> list[SkillMatchSummaryResponse]:
    return list_skills(db, current_user)


@router.get("/skills/{skill_id}", response_model=SkillMatchDetailResponse)
def get_skill_match(skill_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> SkillMatchDetailResponse:
    return get_skill(db, current_user, skill_id)


@router.put("/skills/{skill_id}", response_model=SkillMatchDetailResponse)
def update_skill_match(skill_id: Annotated[int, Path(gt=0)], payload: SkillMatchUpdateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> SkillMatchDetailResponse:
    return update_skill(db, current_user, skill_id, payload)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill_match(skill_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> None:
    delete_skill(db, current_user, skill_id)


@router.post("/history", response_model=AnalysisHistoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_history(payload: AnalysisHistoryCreateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> AnalysisHistoryDetailResponse:
    return create_history(db, current_user, payload)


@router.get("/history", response_model=list[AnalysisHistorySummaryResponse])
def list_analysis_history(current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> list[AnalysisHistorySummaryResponse]:
    return list_history(db, current_user)


@router.get("/history/{history_id}", response_model=AnalysisHistoryDetailResponse)
def get_analysis_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> AnalysisHistoryDetailResponse:
    return get_history(db, current_user, history_id)


@router.put("/history/{history_id}", response_model=AnalysisHistoryDetailResponse)
def update_analysis_history(history_id: Annotated[int, Path(gt=0)], payload: AnalysisHistoryUpdateRequest, current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> AnalysisHistoryDetailResponse:
    return update_history(db, current_user, history_id, payload)


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis_history(history_id: Annotated[int, Path(gt=0)], current_user: CurrentUser, db: JobDescriptionAnalyzerDb) -> None:
    delete_history(db, current_user, history_id)
