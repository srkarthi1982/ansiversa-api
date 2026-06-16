import json
import random
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.memory_trainer.models import (
    MemoryGame,
    MemoryPerformance,
    MemoryRound,
    MemorySession,
)
from app.modules.memory_trainer.schemas import (
    MemoryGameCreateRequest,
    MemoryGameResponse,
    MemoryGameUpdateRequest,
    MemoryPerformanceResponse,
    MemoryProgressResponse,
    MemoryReviewResponse,
    MemoryRoundResponse,
    MemoryRoundSubmitRequest,
    MemorySessionDetailResponse,
    MemorySessionResponse,
)

NUMBER_ITEMS = [str(value) for value in range(10)]
WORD_ITEMS = [
    "river",
    "anchor",
    "orbit",
    "canvas",
    "signal",
    "harbor",
    "planet",
    "window",
    "garden",
    "bridge",
    "forest",
    "summit",
]
COLOR_ITEMS = [
    "red",
    "blue",
    "green",
    "yellow",
    "purple",
    "orange",
    "black",
    "white",
    "teal",
    "pink",
    "gray",
    "gold",
]


def _game_response(game: MemoryGame) -> MemoryGameResponse:
    return MemoryGameResponse.model_validate(game)


def _session_response(session: MemorySession) -> MemorySessionResponse:
    return MemorySessionResponse.model_validate(session)


def _performance_response(
    performance: MemoryPerformance,
) -> MemoryPerformanceResponse:
    return MemoryPerformanceResponse.model_validate(performance)


def _decode_sequence(value: str | None) -> list[str] | None:
    if value is None:
        return None

    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(decoded, list):
        return []

    return [str(item) for item in decoded]


def _encode_sequence(value: list[str]) -> str:
    return json.dumps(value, separators=(",", ":"))


def _round_response(round_: MemoryRound) -> MemoryRoundResponse:
    return MemoryRoundResponse(
        id=round_.id,
        session_id=round_.session_id,
        round_number=round_.round_number,
        sequence=_decode_sequence(round_.sequence) or [],
        user_answer=_decode_sequence(round_.user_answer),
        is_correct=round_.is_correct,
        response_time_ms=round_.response_time_ms,
        created_at=round_.created_at,
        updated_at=round_.updated_at,
    )


def _get_owned_game(db: Session, user: User, game_id: str) -> MemoryGame:
    game = db.get(MemoryGame, game_id)
    if not game or game.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory game was not found.",
        )

    return game


def _get_owned_session(db: Session, user: User, session_id: str) -> MemorySession:
    session = db.get(MemorySession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory session was not found.",
        )

    return session


def _ensure_active_session(session: MemorySession) -> None:
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Completed sessions cannot accept more answers.",
        )


def _list_rounds(db: Session, session_id: str) -> list[MemoryRound]:
    return list(
        db.execute(
            select(MemoryRound)
            .where(MemoryRound.session_id == session_id)
            .order_by(MemoryRound.round_number.asc())
        )
        .scalars()
        .all()
    )


def _get_session_round(
    db: Session,
    session: MemorySession,
    round_number: int,
) -> MemoryRound:
    round_ = db.execute(
        select(MemoryRound).where(
            MemoryRound.session_id == session.id,
            MemoryRound.round_number == round_number,
        )
    ).scalar_one_or_none()
    if not round_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory round was not found for this session.",
        )

    return round_


def _current_round(rounds: list[MemoryRound]) -> MemoryRound | None:
    for round_ in rounds:
        if round_.user_answer is None:
            return round_

    return rounds[-1] if rounds else None


def _generate_sequence(game: MemoryGame) -> list[str]:
    if game.mode == "number_sequence":
        pool = NUMBER_ITEMS
    elif game.mode == "word_sequence":
        pool = WORD_ITEMS
    else:
        pool = COLOR_ITEMS

    return [random.choice(pool) for _ in range(game.sequence_length)]


def _session_detail(
    db: Session,
    session: MemorySession,
) -> MemorySessionDetailResponse:
    game = db.get(MemoryGame, session.game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory game was not found.",
        )

    rounds = _list_rounds(db, session.id)
    current = _current_round(rounds)
    return MemorySessionDetailResponse(
        session=_session_response(session),
        game=_game_response(game),
        rounds=[_round_response(round_) for round_ in rounds],
        current_round=_round_response(current) if current else None,
    )


def list_games(db: Session, user: User) -> list[MemoryGameResponse]:
    games = list(
        db.execute(
            select(MemoryGame)
            .where(MemoryGame.user_id == user.id)
            .order_by(MemoryGame.updated_at.desc(), MemoryGame.title.asc())
        )
        .scalars()
        .all()
    )

    return [_game_response(game) for game in games]


def create_game(
    db: Session,
    user: User,
    payload: MemoryGameCreateRequest,
) -> MemoryGameResponse:
    game = MemoryGame(
        user_id=user.id,
        title=payload.title,
        mode=payload.mode,
        difficulty=payload.difficulty,
        sequence_length=payload.sequence_length,
        round_count=payload.round_count,
        description=payload.description,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    return _game_response(game)


def get_game(db: Session, user: User, game_id: str) -> MemoryGameResponse:
    return _game_response(_get_owned_game(db, user, game_id))


def update_game(
    db: Session,
    user: User,
    game_id: str,
    payload: MemoryGameUpdateRequest,
) -> MemoryGameResponse:
    game = _get_owned_game(db, user, game_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(game, field, value)
    db.commit()
    db.refresh(game)

    return _game_response(game)


def delete_game(db: Session, user: User, game_id: str) -> None:
    game = _get_owned_game(db, user, game_id)
    session_ids = select(MemorySession.id).where(MemorySession.game_id == game.id)
    db.execute(delete(MemoryPerformance).where(MemoryPerformance.session_id.in_(session_ids)))
    db.execute(delete(MemoryRound).where(MemoryRound.session_id.in_(session_ids)))
    db.execute(delete(MemorySession).where(MemorySession.game_id == game.id))
    db.delete(game)
    db.commit()


def start_session(
    db: Session,
    user: User,
    game_id: str,
) -> MemorySessionDetailResponse:
    game = _get_owned_game(db, user, game_id)
    session = MemorySession(user_id=user.id, game_id=game.id)
    db.add(session)
    db.flush()

    for round_number in range(1, game.round_count + 1):
        db.add(
            MemoryRound(
                session_id=session.id,
                round_number=round_number,
                sequence=_encode_sequence(_generate_sequence(game)),
            )
        )

    db.commit()
    db.refresh(session)

    return _session_detail(db, session)


def get_session(
    db: Session,
    user: User,
    session_id: str,
) -> MemorySessionDetailResponse:
    session = _get_owned_session(db, user, session_id)
    return _session_detail(db, session)


def submit_round(
    db: Session,
    user: User,
    session_id: str,
    payload: MemoryRoundSubmitRequest,
) -> MemoryRoundResponse:
    session = _get_owned_session(db, user, session_id)
    _ensure_active_session(session)
    round_ = _get_session_round(db, session, payload.round_number)
    expected = _decode_sequence(round_.sequence) or []
    submitted = payload.user_answer
    round_.user_answer = _encode_sequence(submitted)
    round_.response_time_ms = payload.response_time_ms
    round_.is_correct = [item.lower() for item in submitted] == [
        item.lower() for item in expected
    ]
    db.commit()
    db.refresh(round_)

    return _round_response(round_)


def submit_session(
    db: Session,
    user: User,
    session_id: str,
) -> MemoryPerformanceResponse:
    session = _get_owned_session(db, user, session_id)
    _ensure_active_session(session)
    game = _get_owned_game(db, user, session.game_id)
    rounds = _list_rounds(db, session.id)
    if not rounds:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session has no rounds to submit.",
        )

    total_rounds = len(rounds)
    correct_rounds = sum(1 for round_ in rounds if round_.is_correct is True)
    wrong_rounds = total_rounds - correct_rounds
    response_times = [
        round_.response_time_ms for round_ in rounds if round_.response_time_ms is not None
    ]
    average_response_time_ms = (
        round(sum(response_times) / len(response_times)) if response_times else 0
    )
    completed_at = datetime.now(timezone.utc)
    session.status = "completed"
    session.completed_at = completed_at
    performance = MemoryPerformance(
        user_id=user.id,
        game_id=game.id,
        session_id=session.id,
        total_rounds=total_rounds,
        correct_rounds=correct_rounds,
        wrong_rounds=wrong_rounds,
        accuracy=round((correct_rounds / total_rounds) * 100),
        average_response_time_ms=average_response_time_ms,
        completed_at=completed_at,
    )
    db.add(performance)
    db.commit()
    db.refresh(performance)

    return _performance_response(performance)


def get_review(db: Session, user: User, session_id: str) -> MemoryReviewResponse:
    session = _get_owned_session(db, user, session_id)
    game = _get_owned_game(db, user, session.game_id)
    performance = db.execute(
        select(MemoryPerformance).where(MemoryPerformance.session_id == session.id)
    ).scalar_one_or_none()

    return MemoryReviewResponse(
        session=_session_response(session),
        game=_game_response(game),
        rounds=[_round_response(round_) for round_ in _list_rounds(db, session.id)],
        performance=_performance_response(performance) if performance else None,
    )


def get_progress(db: Session, user: User) -> MemoryProgressResponse:
    performances = list(
        db.execute(
            select(MemoryPerformance).where(MemoryPerformance.user_id == user.id)
        )
        .scalars()
        .all()
    )
    if not performances:
        return MemoryProgressResponse(
            total_sessions=0,
            best_accuracy=0,
            average_accuracy=0,
            total_rounds=0,
            last_completed_at=None,
        )

    total_sessions = len(performances)
    return MemoryProgressResponse(
        total_sessions=total_sessions,
        best_accuracy=max(performance.accuracy for performance in performances),
        average_accuracy=round(
            sum(performance.accuracy for performance in performances) / total_sessions
        ),
        total_rounds=sum(performance.total_rounds for performance in performances),
        last_completed_at=max(performance.completed_at for performance in performances),
    )
