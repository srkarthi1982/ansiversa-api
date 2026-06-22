from dataclasses import dataclass
from typing import Literal, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, load_only

from app.modules.quiz.models import Platform, Roadmap, Subject, Topic


QuizStatusFilter = Literal["all", "active", "inactive"]
QuizSortDirection = Literal["asc", "desc"]
QuizTaxonomyModel = Platform | Subject | Topic | Roadmap
QuizTaxonomyModelType = TypeVar(
    "QuizTaxonomyModelType",
    Platform,
    Subject,
    Topic,
    Roadmap,
)


@dataclass(frozen=True)
class QuizTaxonomyListResult:
    items: list[QuizTaxonomyModel]
    total: int
    page: int
    page_size: int


def _apply_common_filters(
    statement: Select[tuple[QuizTaxonomyModelType]],
    model: type[QuizTaxonomyModelType],
    *,
    q: str | None,
    status_filter: QuizStatusFilter,
    min_questions: int | None,
    max_questions: int | None,
) -> Select[tuple[QuizTaxonomyModelType]]:
    trimmed_q = (q or "").strip()
    if trimmed_q:
        statement = statement.where(model.name.ilike(f"%{trimmed_q}%"))
    if status_filter == "active":
        statement = statement.where(model.is_active.is_(True))
    elif status_filter == "inactive":
        statement = statement.where(model.is_active.is_(False))
    if min_questions is not None:
        statement = statement.where(model.question_count >= min_questions)
    if max_questions is not None:
        statement = statement.where(model.question_count <= max_questions)

    return statement


def _apply_sort(
    statement: Select[tuple[QuizTaxonomyModelType]],
    model: type[QuizTaxonomyModelType],
    sort: str,
    direction: QuizSortDirection,
    sort_options: dict[str, object],
) -> Select[tuple[QuizTaxonomyModelType]]:
    column = sort_options.get(sort, model.id)
    expression = column.desc() if direction == "desc" else column.asc()  # type: ignore[attr-defined]

    if column is model.id:
        return statement.order_by(expression)

    return statement.order_by(expression, model.id.asc())


def _paginate(
    db: Session,
    statement: Select[tuple[QuizTaxonomyModelType]],
    *,
    page: int,
    page_size: int,
) -> QuizTaxonomyListResult:
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = int(db.execute(total_statement).scalar_one())
    items = list(
        db.execute(
            statement.offset((page - 1) * page_size).limit(page_size)
        ).scalars().all()
    )

    return QuizTaxonomyListResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def list_platforms(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    status_filter: QuizStatusFilter,
    sort: str,
    direction: QuizSortDirection,
    min_questions: int | None,
    max_questions: int | None,
    platform_type: str | None,
) -> QuizTaxonomyListResult:
    statement = _apply_common_filters(
        select(Platform).options(
            load_only(
                Platform.id,
                Platform.name,
                Platform.description,
                Platform.type,
                Platform.is_active,
                Platform.question_count,
            )
        ),
        Platform,
        q=q,
        status_filter=status_filter,
        min_questions=min_questions,
        max_questions=max_questions,
    )
    trimmed_type = (platform_type or "").strip()
    if trimmed_type:
        statement = statement.where(Platform.type == trimmed_type)
    statement = _apply_sort(
        statement,
        Platform,
        sort,
        direction,
        {
            "id": Platform.id,
            "name": Platform.name,
            "description": Platform.description,
            "type": Platform.type,
            "qCount": Platform.question_count,
            "status": Platform.is_active,
        },
    )

    return _paginate(db, statement, page=page, page_size=page_size)


def list_subjects(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    status_filter: QuizStatusFilter,
    sort: str,
    direction: QuizSortDirection,
    min_questions: int | None,
    max_questions: int | None,
    platform_id: int | None,
) -> QuizTaxonomyListResult:
    statement = _apply_common_filters(
        select(Subject).options(
            load_only(
                Subject.id,
                Subject.platform_id,
                Subject.name,
                Subject.is_active,
                Subject.question_count,
            )
        ),
        Subject,
        q=q,
        status_filter=status_filter,
        min_questions=min_questions,
        max_questions=max_questions,
    )
    if platform_id is not None:
        statement = statement.where(Subject.platform_id == platform_id)
    statement = _apply_sort(
        statement,
        Subject,
        sort,
        direction,
        {
            "id": Subject.id,
            "name": Subject.name,
            "platformId": Subject.platform_id,
            "qCount": Subject.question_count,
            "status": Subject.is_active,
        },
    )

    return _paginate(db, statement, page=page, page_size=page_size)


def list_topics(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    status_filter: QuizStatusFilter,
    sort: str,
    direction: QuizSortDirection,
    min_questions: int | None,
    max_questions: int | None,
    platform_id: int | None,
    subject_id: int | None,
) -> QuizTaxonomyListResult:
    statement = _apply_common_filters(
        select(Topic).options(
            load_only(
                Topic.id,
                Topic.platform_id,
                Topic.subject_id,
                Topic.name,
                Topic.is_active,
                Topic.question_count,
            )
        ),
        Topic,
        q=q,
        status_filter=status_filter,
        min_questions=min_questions,
        max_questions=max_questions,
    )
    if platform_id is not None:
        statement = statement.where(Topic.platform_id == platform_id)
    if subject_id is not None:
        statement = statement.where(Topic.subject_id == subject_id)
    statement = _apply_sort(
        statement,
        Topic,
        sort,
        direction,
        {
            "id": Topic.id,
            "name": Topic.name,
            "platformId": Topic.platform_id,
            "subjectId": Topic.subject_id,
            "qCount": Topic.question_count,
            "status": Topic.is_active,
        },
    )

    return _paginate(db, statement, page=page, page_size=page_size)


def list_roadmaps(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    status_filter: QuizStatusFilter,
    sort: str,
    direction: QuizSortDirection,
    min_questions: int | None,
    max_questions: int | None,
    platform_id: int | None,
    subject_id: int | None,
    topic_id: int | None,
    roadmap_id: int | None,
) -> QuizTaxonomyListResult:
    statement = _apply_common_filters(
        select(Roadmap).options(
            load_only(
                Roadmap.id,
                Roadmap.platform_id,
                Roadmap.subject_id,
                Roadmap.topic_id,
                Roadmap.name,
                Roadmap.is_active,
                Roadmap.question_count,
            )
        ),
        Roadmap,
        q=q,
        status_filter=status_filter,
        min_questions=min_questions,
        max_questions=max_questions,
    )
    if platform_id is not None:
        statement = statement.where(Roadmap.platform_id == platform_id)
    if subject_id is not None:
        statement = statement.where(Roadmap.subject_id == subject_id)
    if topic_id is not None:
        statement = statement.where(Roadmap.topic_id == topic_id)
    if roadmap_id is not None:
        statement = statement.where(Roadmap.id == roadmap_id)
    statement = _apply_sort(
        statement,
        Roadmap,
        sort,
        direction,
        {
            "id": Roadmap.id,
            "name": Roadmap.name,
            "platformId": Roadmap.platform_id,
            "subjectId": Roadmap.subject_id,
            "topicId": Roadmap.topic_id,
            "qCount": Roadmap.question_count,
            "status": Roadmap.is_active,
        },
    )

    return _paginate(db, statement, page=page, page_size=page_size)
