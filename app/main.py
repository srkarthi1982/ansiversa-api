from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.openapi import generate_operation_id
from app.core.timing import TimingMiddleware, patch_fastapi_serialization_timing
from app.modules.admin.apps_routes import router as admin_apps_router
from app.modules.admin.categories_routes import router as admin_categories_router
from app.modules.admin.faqs_routes import router as admin_faqs_router
from app.modules.admin.routes import router as admin_router
from app.modules.admin.users_routes import router as admin_users_router
from app.modules.ai_translator_and_tone_fixer.routes import router as ai_translator_and_tone_fixer_router
from app.modules.ai_job_interviewer.routes import router as ai_job_interviewer_router
from app.modules.apps.routes import apps_router, categories_router
from app.modules.auth.routes import router as auth_router
from app.modules.book_summary_generator.routes import router as book_summary_generator_router
from app.modules.contact.routes import router as contact_router
from app.modules.prompt_builder.routes import router as prompt_builder_router
from app.modules.snippet_generator.routes import router as snippet_generator_router
from app.modules.social_caption_generator.routes import router as social_caption_generator_router
from app.modules.speech_writer.routes import router as speech_writer_router
from app.modules.ai_notes_summarizer.routes import router as ai_notes_summarizer_router
from app.modules.career_planner.routes import router as career_planner_router
from app.modules.client_feedback_analyzer.routes import router as client_feedback_analyzer_router
from app.modules.concept_explainer.routes import router as concept_explainer_router
from app.modules.contract_generator.routes import router as contract_generator_router
from app.modules.course_tracker.routes import router as course_tracker_router
from app.modules.dashboard.routes import (
    router as dashboard_router,
    summary_router as dashboard_summary_router,
)
from app.modules.dictionary_plus.routes import router as dictionary_plus_router
from app.modules.faqs.routes import router as faqs_router
from app.modules.favorites.routes import router as favorites_router
from app.modules.health.routes import router as health_router
from app.modules.interview_coach.routes import router as interview_coach_router
from app.modules.interview_scheduler.routes import router as interview_scheduler_router
from app.modules.job_description_analyzer.routes import router as job_description_analyzer_router
from app.modules.job_tracker.routes import router as job_tracker_router
from app.modules.lesson_builder.routes import router as lesson_builder_router
from app.modules.linkedin_bio_optimizer.routes import router as linkedin_bio_optimizer_router
from app.modules.memory_trainer.routes import router as memory_trainer_router
from app.modules.meeting_minutes_ai.routes import router as meeting_minutes_ai_router
from app.modules.email_assistant.routes import router as email_assistant_router
from app.modules.invoice_receipt_maker.routes import router as invoice_receipt_maker_router
from app.modules.notifications.routes import router as notifications_router
from app.modules.portfolio_creator.routes import router as portfolio_creator_router
from app.modules.presentation_designer.routes import router as presentation_designer_router
from app.modules.profile.routes import router as profile_router
from app.modules.proposal_writer.routes import router as proposal_writer_router
from app.modules.quiz.routes import router as quiz_router
from app.modules.research_assistant.routes import router as research_assistant_router
from app.modules.resume_builder.routes import router as resume_builder_router
from app.modules.smart_textbook_scanner.routes import router as smart_textbook_scanner_router
from app.modules.study_planner.routes import router as study_planner_router
from app.modules.users.routes import router as users_router
from app.modules.content.routes import router as content_router
from app.modules.visiting_card_maker.routes import router as visiting_card_maker_router

def register_middleware(app: FastAPI) -> None:
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimingMiddleware)


def register_routes(app: FastAPI) -> None:
    app.include_router(
        health_router,
        prefix=f"{settings.API_V1_PREFIX}/health",
        tags=["Health"],
    )
    app.include_router(
        auth_router,
        prefix=f"{settings.API_V1_PREFIX}/auth",
        tags=["Auth"],
    )
    app.include_router(
        apps_router,
        prefix=f"{settings.API_V1_PREFIX}/apps",
        tags=["Apps"],
    )
    app.include_router(
        categories_router,
        prefix=f"{settings.API_V1_PREFIX}/categories",
        tags=["Categories"],
    )
    app.include_router(
        faqs_router,
        prefix=f"{settings.API_V1_PREFIX}/faqs",
        tags=["FAQs"],
    )
    app.include_router(
        contact_router,
        prefix=f"{settings.API_V1_PREFIX}/contact",
        tags=["Contact"],
    )
    app.include_router(
        admin_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin"],
    )
    app.include_router(
        admin_categories_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Categories"],
    )
    app.include_router(
        admin_apps_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Apps"],
    )
    app.include_router(
        admin_users_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin Users"],
    )
    app.include_router(
        admin_faqs_router,
        prefix=f"{settings.API_V1_PREFIX}/admin",
        tags=["Admin FAQs"],
    )
    app.include_router(
        profile_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Profile"],
    )
    app.include_router(
        favorites_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Favorites"],
    )
    app.include_router(
        notifications_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Notifications"],
    )
    app.include_router(
        dashboard_router,
        prefix=f"{settings.API_V1_PREFIX}/me",
        tags=["Dashboard"],
    )
    app.include_router(
        dashboard_summary_router,
        prefix=f"{settings.API_V1_PREFIX}/dashboard",
        tags=["Dashboard"],
    )
    app.include_router(
        users_router,
        prefix=f"{settings.API_V1_PREFIX}/users",
        tags=["Users"],
    )
    app.include_router(
        quiz_router,
        prefix=f"{settings.API_V1_PREFIX}/quiz",
        tags=["Quiz"],
    )
    app.include_router(
        lesson_builder_router,
        prefix=f"{settings.API_V1_PREFIX}/lesson-builder",
        tags=["Lesson Builder"],
    )
    app.include_router(
        memory_trainer_router,
        prefix=f"{settings.API_V1_PREFIX}/memory-trainer",
        tags=["Memory Trainer"],
    )
    app.include_router(
        dictionary_plus_router,
        prefix=f"{settings.API_V1_PREFIX}/dictionary-plus",
        tags=["Dictionary+"],
    )
    app.include_router(
        concept_explainer_router,
        prefix=f"{settings.API_V1_PREFIX}/concept-explainer",
        tags=["Concept Explainer"],
    )
    app.include_router(
        research_assistant_router,
        prefix=f"{settings.API_V1_PREFIX}/research-assistant",
        tags=["Research Assistant"],
    )
    app.include_router(
        ai_notes_summarizer_router,
        prefix=f"{settings.API_V1_PREFIX}/ai-notes-summarizer",
        tags=["AI Notes Summarizer"],
    )
    app.include_router(
        study_planner_router,
        prefix=f"{settings.API_V1_PREFIX}/study-planner",
        tags=["Study Planner"],
    )
    app.include_router(
        course_tracker_router,
        prefix=f"{settings.API_V1_PREFIX}/course-tracker",
        tags=["Course Tracker"],
    )
    app.include_router(
        smart_textbook_scanner_router,
        prefix=f"{settings.API_V1_PREFIX}/smart-textbook-scanner",
        tags=["Smart Textbook Scanner"],
    )
    app.include_router(
        resume_builder_router,
        prefix=f"{settings.API_V1_PREFIX}/resume-builder",
        tags=["Resume Builder"],
    )
    app.include_router(
        visiting_card_maker_router,
        prefix=f"{settings.API_V1_PREFIX}/visiting-card-maker",
        tags=["Visiting Card Maker"],
    )
    app.include_router(
        interview_coach_router,
        prefix=f"{settings.API_V1_PREFIX}/interview-coach",
        tags=["Interview Coach"],
    )
    app.include_router(
        ai_job_interviewer_router,
        prefix=f"{settings.API_V1_PREFIX}/ai-job-interviewer",
        tags=["AI Job Interviewer"],
    )
    app.include_router(
        portfolio_creator_router,
        prefix=f"{settings.API_V1_PREFIX}/portfolio-creator",
        tags=["Portfolio Creator"],
    )
    app.include_router(
        meeting_minutes_ai_router,
        prefix=f"{settings.API_V1_PREFIX}/meeting-minutes-ai",
        tags=["Meeting Minutes AI"],
    )
    app.include_router(
        email_assistant_router,
        prefix=f"{settings.API_V1_PREFIX}/email-assistant",
        tags=["Email Assistant"],
    )
    app.include_router(
        proposal_writer_router,
        prefix=f"{settings.API_V1_PREFIX}/proposal-writer",
        tags=["Proposal Writer"],
    )
    app.include_router(
        invoice_receipt_maker_router,
        prefix=f"{settings.API_V1_PREFIX}/invoice-receipt-maker",
        tags=["Invoice and Receipt Maker"],
    )
    app.include_router(
        contract_generator_router,
        prefix=f"{settings.API_V1_PREFIX}/contract-generator",
        tags=["Contract Generator"],
    )
    app.include_router(
        presentation_designer_router,
        prefix=f"{settings.API_V1_PREFIX}/presentation-designer",
        tags=["Presentation Designer"],
    )
    app.include_router(
        career_planner_router,
        prefix=f"{settings.API_V1_PREFIX}/career-planner",
        tags=["Career Planner"],
    )
    app.include_router(
        linkedin_bio_optimizer_router,
        prefix=f"{settings.API_V1_PREFIX}/linkedin-bio-optimizer",
        tags=["LinkedIn Bio Optimizer"],
    )
    app.include_router(
        client_feedback_analyzer_router,
        prefix=f"{settings.API_V1_PREFIX}/client-feedback-analyzer",
        tags=["Client Feedback Analyzer"],
    )
    app.include_router(
        interview_scheduler_router,
        prefix=f"{settings.API_V1_PREFIX}/interview-scheduler",
        tags=["Interview Scheduler"],
    )
    app.include_router(
        job_tracker_router,
        prefix=f"{settings.API_V1_PREFIX}/job-tracker",
        tags=["Job Tracker"],
    )
    app.include_router(
        job_description_analyzer_router,
        prefix=f"{settings.API_V1_PREFIX}/job-description-analyzer",
        tags=["Job Description Analyzer"],
    )
    app.include_router(
        book_summary_generator_router,
        prefix=f"{settings.API_V1_PREFIX}/book-summary-generator",
        tags=["Book Summary Generator"],
    )
    app.include_router(
        social_caption_generator_router,
        prefix=f"{settings.API_V1_PREFIX}/social-caption-generator",
        tags=["Social Caption Generator"],
    )
    app.include_router(
        speech_writer_router,
        prefix=f"{settings.API_V1_PREFIX}/speech-writer",
        tags=["Speech Writer"],
    )
    app.include_router(
        prompt_builder_router,
        prefix=f"{settings.API_V1_PREFIX}/prompt-builder",
        tags=["Prompt Builder"],
    )
    app.include_router(
        snippet_generator_router,
        prefix=f"{settings.API_V1_PREFIX}/snippet-generator",
        tags=["Snippet Generator"],
    )
    app.include_router(
        ai_translator_and_tone_fixer_router,
        prefix=f"{settings.API_V1_PREFIX}/ai-translator-and-tone-fixer",
        tags=["AI Translator and Tone Fixer"],
    )
    app.include_router(
        content_router, 
        prefix="/api/v1",
        tags=["content"],
    )

    @app.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "status": "running",
            "version": settings.APP_VERSION,
        }


def create_app() -> FastAPI:
    patch_fastapi_serialization_timing()
    app = FastAPI(
        title=settings.APP_NAME,
        description="Single source of truth API for the Ansiversa ecosystem.",
        version=settings.APP_VERSION,
        generate_unique_id_function=generate_operation_id,
    )

    register_middleware(app)
    register_routes(app)

    return app


app = create_app()
