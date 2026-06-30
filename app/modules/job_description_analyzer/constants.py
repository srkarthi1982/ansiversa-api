MODULE_SLUG = "job-description-analyzer"
MODULE_NAME = "Job Description Analyzer"
TIMING_LABEL = "job_description_analyzer"
VERSION_TABLE = "job_description_analyzer_alembic_version"

MANAGED_TABLES = {
    "JobDescriptions",
    "JobAnalyses",
    "SkillMatches",
    "AnalysisHistory",
}
