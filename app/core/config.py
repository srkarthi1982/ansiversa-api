from typing import Annotated, Any, Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


DEFAULT_CORS_ORIGINS = [
    "http://localhost:4321",
    "https://qa.ansiversa.com",
    "https://ansiversa.com",
    "https://www.ansiversa.com",
]


class Settings(BaseSettings):
    APP_NAME: str = "Ansiversa API"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    PARENT_DATABASE_URL: str = "sqlite:///./ansiversa_api.db"
    TURSO_AUTH_TOKEN: str | None = None
    QUIZ_DATABASE_URL: str = "sqlite:///./quiz.db"
    LESSON_BUILDER_DATABASE_URL: str = "sqlite:///./lesson_builder.db"
    MEMORY_TRAINER_DATABASE_URL: str = "sqlite:///./memory_trainer.db"
    DICTIONARY_PLUS_DATABASE_URL: str = "sqlite:///./dictionary_plus.db"
    CONCEPT_EXPLAINER_DATABASE_URL: str = "sqlite:///./concept_explainer.db"
    RESEARCH_ASSISTANT_DATABASE_URL: str = "sqlite:///./research_assistant.db"
    AI_NOTES_SUMMARIZER_DATABASE_URL: str = "sqlite:///./ai_notes_summarizer.db"
    STUDY_PLANNER_DATABASE_URL: str = "sqlite:///./study_planner.db"
    COURSE_TRACKER_DATABASE_URL: str = "sqlite:///./course_tracker.db"
    SMART_TEXTBOOK_SCANNER_DATABASE_URL: str = "sqlite:///./smart_textbook_scanner.db"
    RESUME_BUILDER_DATABASE_URL: str = "sqlite:///./resume_builder.db"
    VISITING_CARD_MAKER_DATABASE_URL: str = "sqlite:///./visiting_card_maker.db"
    INTERVIEW_COACH_DATABASE_URL: str = "sqlite:///./interview_coach.db"
    AI_JOB_INTERVIEWER_DATABASE_URL: str = "sqlite:///./ai_job_interviewer.db"
    PORTFOLIO_CREATOR_DATABASE_URL: str = "sqlite:///./portfolio_creator.db"
    MEETING_MINUTES_AI_DATABASE_URL: str = "sqlite:///./meeting_minutes_ai.db"
    EMAIL_ASSISTANT_DATABASE_URL: str = "sqlite:///./email_assistant.db"
    PROPOSAL_WRITER_DATABASE_URL: str = "sqlite:///./proposal_writer.db"
    QUIZ_ATTEMPT_EXPIRE_HOURS: int = Field(default=2, gt=0, le=24)
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    ANSIVERSA_AUTH_SECRET: str = "dev-ansiversa-auth-secret"
    AUTH_COOKIE_NAME: str = "ansiversa_session"
    AUTH_COOKIE_DOMAIN: str | None = None
    AUTH_COOKIE_SECURE: bool | None = None
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = None
    AUTH_COOKIE_MAX_AGE_SECONDS: int | None = Field(default=None, gt=0)
    API_TIMING_ENABLED: bool = True
    CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS.copy()
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]

        if isinstance(value, (list, tuple, set)):
            return [str(origin).strip() for origin in value if str(origin).strip()]

        return value

    @field_validator("AUTH_COOKIE_DOMAIN", mode="before")
    @classmethod
    def parse_auth_cookie_domain(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None

        return value

    @model_validator(mode="after")
    def set_auth_cookie_defaults(self) -> Self:
        is_production = self.APP_ENV.strip().lower() == "production"

        if "*" in self.CORS_ORIGINS:
            raise ValueError(
                "CORS_ORIGINS must not contain '*' when credentials are enabled."
            )
        for origin in DEFAULT_CORS_ORIGINS:
            if origin not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(origin)
        if self.AUTH_COOKIE_DOMAIN is None and is_production:
            self.AUTH_COOKIE_DOMAIN = ".ansiversa.com"
        if self.AUTH_COOKIE_SECURE is None:
            self.AUTH_COOKIE_SECURE = is_production
        if self.AUTH_COOKIE_SAMESITE is None:
            self.AUTH_COOKIE_SAMESITE = "none" if is_production else "lax"
        if self.AUTH_COOKIE_MAX_AGE_SECONDS is None:
            self.AUTH_COOKIE_MAX_AGE_SECONDS = self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return self


settings = Settings()
