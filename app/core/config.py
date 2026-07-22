from typing import Annotated, Any, Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


DEFAULT_CORS_ORIGINS = [
    "http://localhost:4321",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://qa.ansiversa.com",
    "https://ansiversa.com",
    "https://www.ansiversa.com",
]

DEFAULT_INVOICE_RECEIPT_MAKER_DATABASE_URL = "sqlite:///./invoice_receipt_maker.db"
PRODUCTION_INVOICE_RECEIPT_MAKER_DATABASE_URL = (
    "libsql://invoice-and-receipt-maker-ansiversa.aws-ap-south-1.turso.io"
)
DEFAULT_WELLNESS_AND_GOAL_PLANNER_DATABASE_URL = "sqlite:///./wellness_and_goal_planner.db"
PRODUCTION_WELLNESS_AND_GOAL_PLANNER_DATABASE_URL = (
    "libsql://wellness-and-goal-planner-ansiversa.aws-ap-south-1.turso.io"
)
DEFAULT_GOAL_TRACKER_DATABASE_URL = "sqlite:///./goal_tracker.db"
DEFAULT_MEAL_PLANNER_DATABASE_URL = "sqlite:///./meal_planner.db"
DEFAULT_FITNESS_TRACKER_DATABASE_URL = "sqlite:///./fitness_tracker.db"
DEFAULT_LANGUAGE_LEARNING_BUDDY_DATABASE_URL = "sqlite:///./language_learning_buddy.db"
DEFAULT_MEDICINE_REMINDER_DATABASE_URL = "sqlite:///./medicine_reminder.db"
DEFAULT_HEALTH_REPORT_ORGANIZER_DATABASE_URL = "sqlite:///./health_report_organizer.db"
DEFAULT_FAMILY_TASK_PLANNER_DATABASE_URL = "sqlite:///./family_task_planner.db"
DEFAULT_RENT_A_CAR_DATABASE_URL = "sqlite:///./rent_a_car.db"
DEFAULT_CAR_POOL_DATABASE_URL = "sqlite:///./car_pool.db"
DEFAULT_VEHICLE_MAINTENANCE_TRACKER_DATABASE_URL = "sqlite:///./vehicle_maintenance_tracker.db"
DEFAULT_PARKING_EXPENSE_TRACKER_DATABASE_URL = "sqlite:///./parking_expense_tracker.db"
DEFAULT_TRIP_COST_CALCULATOR_DATABASE_URL = "sqlite:///./trip_cost_calculator.db"
DEFAULT_CORPORATE_TAX_UAE_DATABASE_URL = "sqlite:///./corporate_tax_uae.db"
DEFAULT_VAT_ASSISTANT_UAE_DATABASE_URL = "sqlite:///./vat_assistant_uae.db"
DEFAULT_SCHOOL_ADMINISTRATION_DATABASE_URL = "sqlite:///./school_administration.db"
DEFAULT_SUBSCRIPTION_MANAGER_DATABASE_URL = "sqlite:///./subscription_manager.db"
DEFAULT_EMI_LOAN_CALCULATOR_DATABASE_URL = "sqlite:///./emi_loan_calculator.db"
DEFAULT_DOCUMENT_EXPIRY_TRACKER_DATABASE_URL = "sqlite:///./document_expiry_tracker.db"
DEFAULT_DIGITAL_DOCUMENT_VAULT_DATABASE_URL = "sqlite:///./digital_document_vault.db"
DEFAULT_HOME_INVENTORY_MANAGER_DATABASE_URL = "sqlite:///./home_inventory_manager.db"
DEFAULT_HOUSEHOLD_EXPENSE_SPLITTER_DATABASE_URL = "sqlite:///./household_expense_splitter.db"
DEFAULT_EMERGENCY_CONTACTS_ORGANIZER_DATABASE_URL = "sqlite:///./emergency_contacts_organizer.db"
DEFAULT_PACKING_CHECKLIST_DATABASE_URL = "sqlite:///./packing_checklist.db"
DEFAULT_BIRTHDAY_AND_ANNIVERSARY_REMINDER_DATABASE_URL = "sqlite:///./birthday_and_anniversary_reminder.db"
DEFAULT_HOME_MAINTENANCE_PLANNER_DATABASE_URL = "sqlite:///./home_maintenance_planner.db"
DEFAULT_DOCTOR_VISIT_TRACKER_DATABASE_URL = "sqlite:///./doctor_visit_tracker.db"
DEFAULT_WATER_INTAKE_TRACKER_DATABASE_URL = "sqlite:///./water_intake_tracker.db"
DEFAULT_VACCINATION_TRACKER_DATABASE_URL = "sqlite:///./vaccination_tracker.db"
DEFAULT_SYMPTOM_JOURNAL_DATABASE_URL = "sqlite:///./symptom_journal.db"
DEFAULT_FIRST_AID_GUIDE_DATABASE_URL = "sqlite:///./first_aid_guide.db"
DEFAULT_FUEL_EXPENSE_TRACKER_DATABASE_URL = "sqlite:///./fuel_expense_tracker.db"
DEFAULT_DRIVER_LOGBOOK_DATABASE_URL = "sqlite:///./driver_logbook.db"
DEFAULT_VEHICLE_DOCUMENT_TRACKER_DATABASE_URL = "sqlite:///./vehicle_document_tracker.db"
DEFAULT_MEETING_SCHEDULER_DATABASE_URL = "sqlite:///./meeting_scheduler.db"
DEFAULT_LEAVE_PLANNER_DATABASE_URL = "sqlite:///./leave_planner.db"
DEFAULT_SHIFT_PLANNER_DATABASE_URL = "sqlite:///./shift_planner.db"
DEFAULT_WORK_LOG_TRACKER_DATABASE_URL = "sqlite:///./work_log_tracker.db"
DEFAULT_BILL_SPLITTER_DATABASE_URL = "sqlite:///./bill_splitter.db"
DEFAULT_SAVINGS_GOAL_PLANNER_DATABASE_URL = "sqlite:///./savings_goal_planner.db"
DEFAULT_SALARY_BREAKDOWN_CALCULATOR_DATABASE_URL = "sqlite:///./salary_breakdown_calculator.db"
DEFAULT_NET_WORTH_TRACKER_DATABASE_URL = "sqlite:///./net_worth_tracker.db"
DEFAULT_DECISION_MAKER_DATABASE_URL = "sqlite:///./decision_maker.db"
DEFAULT_ERRAND_PLANNER_DATABASE_URL = "sqlite:///./errand_planner.db"
DEFAULT_LOCAL_SERVICES_FINDER_DATABASE_URL = "sqlite:///./local_services_finder.db"
DEFAULT_EMERGENCY_CHECKLIST_DATABASE_URL = "sqlite:///./emergency_checklist.db"
DEFAULT_TRAVEL_ITINERARY_BUILDER_DATABASE_URL = "sqlite:///./travel_itinerary_builder.db"


class Settings(BaseSettings):
    APP_NAME: str = "Ansiversa API"
    APP_ENV: str = "development"
    VERCEL_ENV: str | None = None
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
    INVOICE_RECEIPT_MAKER_DATABASE_URL: str = DEFAULT_INVOICE_RECEIPT_MAKER_DATABASE_URL
    CONTRACT_GENERATOR_DATABASE_URL: str = "sqlite:///./contract_generator.db"
    PRESENTATION_DESIGNER_DATABASE_URL: str = "sqlite:///./presentation_designer.db"
    CAREER_PLANNER_DATABASE_URL: str = "sqlite:///./career_planner.db"
    LINKEDIN_BIO_OPTIMIZER_DATABASE_URL: str = "sqlite:///./linkedin_bio_optimizer.db"
    CLIENT_FEEDBACK_ANALYZER_DATABASE_URL: str = "sqlite:///./client_feedback_analyzer.db"
    INTERVIEW_SCHEDULER_DATABASE_URL: str = "sqlite:///./interview_scheduler.db"
    JOB_TRACKER_DATABASE_URL: str = "sqlite:///./job_tracker.db"
    JOB_DESCRIPTION_ANALYZER_DATABASE_URL: str = "sqlite:///./job_description_analyzer.db"
    BOOK_SUMMARY_GENERATOR_DATABASE_URL: str = "sqlite:///./book_summary_generator.db"
    SOCIAL_CAPTION_GENERATOR_DATABASE_URL: str = "sqlite:///./social_caption_generator.db"
    SPEECH_WRITER_DATABASE_URL: str = "sqlite:///./speech_writer.db"
    PROMPT_BUILDER_DATABASE_URL: str = "sqlite:///./prompt_builder.db"
    SNIPPET_GENERATOR_DATABASE_URL: str = "sqlite:///./snippet_generator.db"
    AI_TRANSLATOR_AND_TONE_FIXER_DATABASE_URL: str = "sqlite:///./ai_translator_and_tone_fixer.db"
    GRAMMAR_AND_PARAPHRASING_ASSISTANT_DATABASE_URL: str = "sqlite:///./grammar_and_paraphrasing_assistant.db"
    CREATIVE_TITLE_GENERATOR_DATABASE_URL: str = "sqlite:///./creative_title_generator.db"
    PROJECT_TRACKER_DATABASE_URL: str = "sqlite:///./project_tracker.db"
    TASK_PRIORITIZER_DATABASE_URL: str = "sqlite:///./task_prioritizer.db"
    EXPENSE_TRACKER_DATABASE_URL: str = "sqlite:///./expense_tracker.db"
    WELLNESS_AND_GOAL_PLANNER_DATABASE_URL: str = DEFAULT_WELLNESS_AND_GOAL_PLANNER_DATABASE_URL
    GOAL_TRACKER_DATABASE_URL: str = DEFAULT_GOAL_TRACKER_DATABASE_URL
    MEAL_PLANNER_DATABASE_URL: str = DEFAULT_MEAL_PLANNER_DATABASE_URL
    FITNESS_TRACKER_DATABASE_URL: str = DEFAULT_FITNESS_TRACKER_DATABASE_URL
    LANGUAGE_LEARNING_BUDDY_DATABASE_URL: str = DEFAULT_LANGUAGE_LEARNING_BUDDY_DATABASE_URL
    MEDICINE_REMINDER_DATABASE_URL: str = DEFAULT_MEDICINE_REMINDER_DATABASE_URL
    HEALTH_REPORT_ORGANIZER_DATABASE_URL: str = DEFAULT_HEALTH_REPORT_ORGANIZER_DATABASE_URL
    FAMILY_TASK_PLANNER_DATABASE_URL: str = DEFAULT_FAMILY_TASK_PLANNER_DATABASE_URL
    RENT_A_CAR_DATABASE_URL: str = DEFAULT_RENT_A_CAR_DATABASE_URL
    CAR_POOL_DATABASE_URL: str = DEFAULT_CAR_POOL_DATABASE_URL
    VEHICLE_MAINTENANCE_TRACKER_DATABASE_URL: str = DEFAULT_VEHICLE_MAINTENANCE_TRACKER_DATABASE_URL
    PARKING_EXPENSE_TRACKER_DATABASE_URL: str = DEFAULT_PARKING_EXPENSE_TRACKER_DATABASE_URL
    TRIP_COST_CALCULATOR_DATABASE_URL: str = DEFAULT_TRIP_COST_CALCULATOR_DATABASE_URL
    CORPORATE_TAX_UAE_DATABASE_URL: str = DEFAULT_CORPORATE_TAX_UAE_DATABASE_URL
    VAT_ASSISTANT_UAE_DATABASE_URL: str = DEFAULT_VAT_ASSISTANT_UAE_DATABASE_URL
    SCHOOL_ADMINISTRATION_DATABASE_URL: str = DEFAULT_SCHOOL_ADMINISTRATION_DATABASE_URL
    SUBSCRIPTION_MANAGER_DATABASE_URL: str = DEFAULT_SUBSCRIPTION_MANAGER_DATABASE_URL
    EMI_LOAN_CALCULATOR_DATABASE_URL: str = DEFAULT_EMI_LOAN_CALCULATOR_DATABASE_URL
    DOCUMENT_EXPIRY_TRACKER_DATABASE_URL: str = DEFAULT_DOCUMENT_EXPIRY_TRACKER_DATABASE_URL
    DIGITAL_DOCUMENT_VAULT_DATABASE_URL: str = DEFAULT_DIGITAL_DOCUMENT_VAULT_DATABASE_URL
    HOME_INVENTORY_MANAGER_DATABASE_URL: str = DEFAULT_HOME_INVENTORY_MANAGER_DATABASE_URL
    HOUSEHOLD_EXPENSE_SPLITTER_DATABASE_URL: str = DEFAULT_HOUSEHOLD_EXPENSE_SPLITTER_DATABASE_URL
    EMERGENCY_CONTACTS_ORGANIZER_DATABASE_URL: str = DEFAULT_EMERGENCY_CONTACTS_ORGANIZER_DATABASE_URL
    PACKING_CHECKLIST_DATABASE_URL: str = DEFAULT_PACKING_CHECKLIST_DATABASE_URL
    BIRTHDAY_AND_ANNIVERSARY_REMINDER_DATABASE_URL: str = DEFAULT_BIRTHDAY_AND_ANNIVERSARY_REMINDER_DATABASE_URL
    HOME_MAINTENANCE_PLANNER_DATABASE_URL: str = DEFAULT_HOME_MAINTENANCE_PLANNER_DATABASE_URL
    DOCTOR_VISIT_TRACKER_DATABASE_URL: str = DEFAULT_DOCTOR_VISIT_TRACKER_DATABASE_URL
    WATER_INTAKE_TRACKER_DATABASE_URL: str = DEFAULT_WATER_INTAKE_TRACKER_DATABASE_URL
    VACCINATION_TRACKER_DATABASE_URL: str = DEFAULT_VACCINATION_TRACKER_DATABASE_URL
    SYMPTOM_JOURNAL_DATABASE_URL: str = DEFAULT_SYMPTOM_JOURNAL_DATABASE_URL
    FIRST_AID_GUIDE_DATABASE_URL: str = DEFAULT_FIRST_AID_GUIDE_DATABASE_URL
    FUEL_EXPENSE_TRACKER_DATABASE_URL: str = DEFAULT_FUEL_EXPENSE_TRACKER_DATABASE_URL
    DRIVER_LOGBOOK_DATABASE_URL: str = DEFAULT_DRIVER_LOGBOOK_DATABASE_URL
    VEHICLE_DOCUMENT_TRACKER_DATABASE_URL: str = DEFAULT_VEHICLE_DOCUMENT_TRACKER_DATABASE_URL
    MEETING_SCHEDULER_DATABASE_URL: str = DEFAULT_MEETING_SCHEDULER_DATABASE_URL
    LEAVE_PLANNER_DATABASE_URL: str = DEFAULT_LEAVE_PLANNER_DATABASE_URL
    SHIFT_PLANNER_DATABASE_URL: str = DEFAULT_SHIFT_PLANNER_DATABASE_URL
    WORK_LOG_TRACKER_DATABASE_URL: str = DEFAULT_WORK_LOG_TRACKER_DATABASE_URL
    BILL_SPLITTER_DATABASE_URL: str = DEFAULT_BILL_SPLITTER_DATABASE_URL
    SAVINGS_GOAL_PLANNER_DATABASE_URL: str = DEFAULT_SAVINGS_GOAL_PLANNER_DATABASE_URL
    SALARY_BREAKDOWN_CALCULATOR_DATABASE_URL: str = DEFAULT_SALARY_BREAKDOWN_CALCULATOR_DATABASE_URL
    NET_WORTH_TRACKER_DATABASE_URL: str = DEFAULT_NET_WORTH_TRACKER_DATABASE_URL
    DECISION_MAKER_DATABASE_URL: str = DEFAULT_DECISION_MAKER_DATABASE_URL
    ERRAND_PLANNER_DATABASE_URL: str = DEFAULT_ERRAND_PLANNER_DATABASE_URL
    LOCAL_SERVICES_FINDER_DATABASE_URL: str = DEFAULT_LOCAL_SERVICES_FINDER_DATABASE_URL
    EMERGENCY_CHECKLIST_DATABASE_URL: str = DEFAULT_EMERGENCY_CHECKLIST_DATABASE_URL
    TRAVEL_ITINERARY_BUILDER_DATABASE_URL: str = DEFAULT_TRAVEL_ITINERARY_BUILDER_DATABASE_URL
    QUIZ_ATTEMPT_EXPIRE_HOURS: int = Field(default=2, gt=0, le=24)
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)
    ANSIVERSA_AUTH_SECRET: str = "dev-ansiversa-auth-secret"
    AUTH_COOKIE_NAME: str = "ansiversa_session"
    AUTH_SESSION_HINT_COOKIE_NAME: str = "ansiversa_has_session"
    AUTH_COOKIE_DOMAIN: str | None = None
    AUTH_COOKIE_SECURE: bool | None = None
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] | None = None
    AUTH_COOKIE_MAX_AGE_SECONDS: int | None = Field(default=None, gt=0)
    API_TIMING_ENABLED: bool = True
    AI_GATEWAY_ENABLED: bool = True
    OPENAI_API_KEY: str | None = None
    ASSISTANT_OPENAI_ENABLED: bool = True
    ASSISTANT_OPENAI_MODEL: str = "gpt-4.1-mini"
    ASSISTANT_OPENAI_TIMEOUT_SECONDS: float = Field(default=20.0, gt=0, le=60)
    ASSISTANT_OPENAI_MAX_OUTPUT_TOKENS: int = Field(default=600, ge=64, le=2000)
    ASSISTANT_OPENAI_TEMPERATURE: float = Field(default=0.2, ge=0, le=2)
    AI_MAX_CONTEXT_CHUNKS: int = Field(default=5, ge=1, le=10)
    AI_MAX_USER_MESSAGE_LENGTH: int = Field(default=2000, ge=1, le=5000)
    AI_DEBUG: bool = False
    ASSISTANT_MAX_CONTEXT_CHARS: int = Field(default=3500, ge=500, le=10000)
    ASTRA_PERSONAL_DATA_TOOLS_ENABLED: bool = False
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
        is_production = (
            self.APP_ENV.strip().lower() == "production"
            or (self.VERCEL_ENV or "").strip().lower() == "production"
        )

        if "*" in self.CORS_ORIGINS:
            raise ValueError(
                "CORS_ORIGINS must not contain '*' when credentials are enabled."
            )
        if (
            is_production
            and self.INVOICE_RECEIPT_MAKER_DATABASE_URL
            == DEFAULT_INVOICE_RECEIPT_MAKER_DATABASE_URL
        ):
            self.INVOICE_RECEIPT_MAKER_DATABASE_URL = (
                PRODUCTION_INVOICE_RECEIPT_MAKER_DATABASE_URL
            )
        if (
            is_production
            and self.WELLNESS_AND_GOAL_PLANNER_DATABASE_URL
            == DEFAULT_WELLNESS_AND_GOAL_PLANNER_DATABASE_URL
        ):
            self.WELLNESS_AND_GOAL_PLANNER_DATABASE_URL = (
                PRODUCTION_WELLNESS_AND_GOAL_PLANNER_DATABASE_URL
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
