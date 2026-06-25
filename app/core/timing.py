from __future__ import annotations

import contextvars
import hashlib
import json
import logging
import time
from collections import Counter
from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from typing import Any, TypeVar

import fastapi.routing
from sqlalchemy import Engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, sessionmaker
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings


T = TypeVar("T")

logger = logging.getLogger("uvicorn.error")
_active_timing: contextvars.ContextVar["RequestTiming | None"] = contextvars.ContextVar(
    "active_request_timing",
    default=None,
)
_session_operation_depth: contextvars.ContextVar[int] = contextvars.ContextVar(
    "session_operation_depth",
    default=0,
)
_serialize_response = fastapi.routing.serialize_response
_json_response_render = JSONResponse.render
_serialization_patched = False
_registered_engine_ids: set[int] = set()


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000


def _rounded(value: float) -> float:
    return round(value, 3)


def _statement_key(statement: str) -> str:
    normalized = " ".join(statement.split())
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]


def _statement_preview(statement: str, limit: int = 160) -> str:
    normalized = " ".join(statement.split())
    return normalized[:limit]


@dataclass
class StatementTiming:
    database: str
    statement_hash: str
    statement: str
    count: int = 0
    duration_ms: float = 0.0


@dataclass
class RequestTiming:
    method: str
    path: str
    start: float = field(default_factory=time.perf_counter)
    session_create_ms: float = 0.0
    session_close_ms: float = 0.0
    raw_db_ms: float = 0.0
    session_execute_ms: float = 0.0
    session_scalar_ms: float = 0.0
    session_scalars_ms: float = 0.0
    session_get_ms: float = 0.0
    commit_ms: float = 0.0
    flush_ms: float = 0.0
    refresh_ms: float = 0.0
    pydantic_serialize_ms: float = 0.0
    response_json_render_ms: float = 0.0
    orm_objects_loaded: int = 0
    query_count: int = 0
    commit_count: int = 0
    flush_count: int = 0
    refresh_count: int = 0
    session_count: int = 0
    db_operation_count: int = 0
    statements: dict[str, StatementTiming] = field(default_factory=dict)
    session_labels: Counter[str] = field(default_factory=Counter)
    db_labels: Counter[str] = field(default_factory=Counter)

    def record_statement(
        self,
        *,
        database: str,
        statement: str,
        duration_ms: float,
    ) -> None:
        statement_hash = _statement_key(statement)
        key = f"{database}:{statement_hash}"
        timing = self.statements.get(key)
        if timing is None:
            timing = StatementTiming(
                database=database,
                statement_hash=statement_hash,
                statement=_statement_preview(statement),
            )
            self.statements[key] = timing
        timing.count += 1
        timing.duration_ms += duration_ms
        self.query_count += 1
        self.raw_db_ms += duration_ms
        self.db_labels[database] += 1

    def summary(self, *, status_code: int | None, total_ms: float) -> dict[str, Any]:
        duplicate_queries = sum(
            statement.count - 1
            for statement in self.statements.values()
            if statement.count > 1
        )
        top_queries = sorted(
            self.statements.values(),
            key=lambda statement: statement.duration_ms,
            reverse=True,
        )[:5]
        db_session_wall_ms = (
            self.session_execute_ms
            + self.session_scalar_ms
            + self.session_scalars_ms
            + self.session_get_ms
        )
        sqlalchemy_python_gap_ms = max(db_session_wall_ms - self.raw_db_ms, 0.0)
        response_build_ms = self.pydantic_serialize_ms + self.response_json_render_ms

        return {
            "method": self.method,
            "path": self.path,
            "status_code": status_code,
            "total_ms": _rounded(total_ms),
            "db_raw_execute_ms": _rounded(self.raw_db_ms),
            "sqlalchemy_session_call_ms": _rounded(db_session_wall_ms),
            "sqlalchemy_python_gap_ms": _rounded(sqlalchemy_python_gap_ms),
            "orm_objects_loaded": self.orm_objects_loaded,
            "pydantic_serialize_ms": _rounded(self.pydantic_serialize_ms),
            "response_json_render_ms": _rounded(self.response_json_render_ms),
            "response_build_ms": _rounded(response_build_ms),
            "commit_ms": _rounded(self.commit_ms),
            "flush_ms": _rounded(self.flush_ms),
            "refresh_ms": _rounded(self.refresh_ms),
            "session_create_ms": _rounded(self.session_create_ms),
            "session_close_ms": _rounded(self.session_close_ms),
            "query_count": self.query_count,
            "duplicate_query_count": duplicate_queries,
            "commit_count": self.commit_count,
            "flush_count": self.flush_count,
            "refresh_count": self.refresh_count,
            "session_count": self.session_count,
            "session_labels": dict(self.session_labels),
            "db_labels": dict(self.db_labels),
            "top_queries": [
                {
                    "database": statement.database,
                    "hash": statement.statement_hash,
                    "count": statement.count,
                    "duration_ms": _rounded(statement.duration_ms),
                    "statement": statement.statement,
                }
                for statement in top_queries
            ],
        }


class TimingSession(Session):
    def _time_operation(self, field_name: str, operation: Callable[[], T]) -> T:
        timing = _active_timing.get()
        depth = _session_operation_depth.get()
        if timing is None or depth > 0:
            return operation()

        token = _session_operation_depth.set(depth + 1)
        start = time.perf_counter()
        try:
            return operation()
        finally:
            setattr(timing, field_name, getattr(timing, field_name) + _elapsed_ms(start))
            timing.db_operation_count += 1
            _session_operation_depth.reset(token)

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return self._time_operation(
            "session_execute_ms",
            lambda: Session.execute(self, *args, **kwargs),
        )

    def scalar(self, *args: Any, **kwargs: Any) -> Any:
        return self._time_operation(
            "session_scalar_ms",
            lambda: Session.scalar(self, *args, **kwargs),
        )

    def scalars(self, *args: Any, **kwargs: Any) -> Any:
        return self._time_operation(
            "session_scalars_ms",
            lambda: Session.scalars(self, *args, **kwargs),
        )

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._time_operation(
            "session_get_ms",
            lambda: Session.get(self, *args, **kwargs),
        )

    def commit(self) -> None:
        timing = _active_timing.get()
        depth = _session_operation_depth.get()
        if timing is None or depth > 0:
            return super().commit()

        token = _session_operation_depth.set(depth + 1)
        start = time.perf_counter()
        try:
            return super().commit()
        finally:
            timing.commit_ms += _elapsed_ms(start)
            timing.commit_count += 1
            _session_operation_depth.reset(token)

    def flush(self, objects: Any = None) -> None:
        timing = _active_timing.get()
        depth = _session_operation_depth.get()
        if timing is None or depth > 0:
            return super().flush(objects=objects)

        token = _session_operation_depth.set(depth + 1)
        start = time.perf_counter()
        try:
            return super().flush(objects=objects)
        finally:
            timing.flush_ms += _elapsed_ms(start)
            timing.flush_count += 1
            _session_operation_depth.reset(token)

    def refresh(self, *args: Any, **kwargs: Any) -> None:
        timing = _active_timing.get()
        depth = _session_operation_depth.get()
        if timing is None or depth > 0:
            return super().refresh(*args, **kwargs)

        token = _session_operation_depth.set(depth + 1)
        start = time.perf_counter()
        try:
            return super().refresh(*args, **kwargs)
        finally:
            timing.refresh_ms += _elapsed_ms(start)
            timing.refresh_count += 1
            _session_operation_depth.reset(token)


@event.listens_for(TimingSession, "loaded_as_persistent")
def _record_orm_load(session: TimingSession, instance: object) -> None:
    _ = session, instance
    timing = _active_timing.get()
    if timing is not None:
        timing.orm_objects_loaded += 1


def register_timing_engine(engine: Engine, database_label: str) -> None:
    engine_id = id(engine)
    if engine_id in _registered_engine_ids:
        return

    @event.listens_for(engine, "before_cursor_execute")
    def _before_cursor_execute(
        conn: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        _ = cursor, parameters, executemany
        timing_stack = conn.info.setdefault("timing_query_start", [])
        timing_stack.append(time.perf_counter())
        setattr(context, "_ansiversa_timing_statement", statement)

    @event.listens_for(engine, "after_cursor_execute")
    def _after_cursor_execute(
        conn: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: object,
        executemany: bool,
    ) -> None:
        _ = cursor, parameters, context, executemany
        timing_stack = conn.info.get("timing_query_start", [])
        start = timing_stack.pop() if timing_stack else None
        timing = _active_timing.get()
        if start is None or timing is None:
            return

        timing.record_statement(
            database=database_label,
            statement=statement,
            duration_ms=_elapsed_ms(start),
        )

    _registered_engine_ids.add(engine_id)


def get_timed_db(
    session_factory: sessionmaker[TimingSession],
    session_label: str,
) -> Generator[TimingSession, None, None]:
    timing = _active_timing.get()
    start = time.perf_counter()
    db = session_factory()
    if timing is not None:
        timing.session_create_ms += _elapsed_ms(start)
        timing.session_count += 1
        timing.session_labels[session_label] += 1

    try:
        yield db
    finally:
        close_start = time.perf_counter()
        db.close()
        if timing is not None:
            timing.session_close_ms += _elapsed_ms(close_start)


def patch_fastapi_serialization_timing() -> None:
    global _serialization_patched

    if _serialization_patched:
        return

    async def timed_serialize_response(*args: Any, **kwargs: Any) -> Any:
        timing = _active_timing.get()
        start = time.perf_counter()
        try:
            return await _serialize_response(*args, **kwargs)
        finally:
            if timing is not None:
                timing.pydantic_serialize_ms += _elapsed_ms(start)

    def timed_json_response_render(self: JSONResponse, content: Any) -> bytes:
        timing = _active_timing.get()
        start = time.perf_counter()
        try:
            return _json_response_render(self, content)
        finally:
            if timing is not None:
                timing.response_json_render_ms += _elapsed_ms(start)

    fastapi.routing.serialize_response = timed_serialize_response
    JSONResponse.render = timed_json_response_render
    _serialization_patched = True


class TimingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not settings.API_TIMING_ENABLED:
            await self.app(scope, receive, send)
            return

        timing = RequestTiming(
            method=str(scope.get("method", "")),
            path=str(scope.get("path", "")),
        )
        token = _active_timing.set(timing)
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            self._log_timing(timing, status_code)
            _active_timing.reset(token)

    @staticmethod
    def _log_timing(timing: RequestTiming, status_code: int | None) -> None:
        total_ms = _elapsed_ms(timing.start)
        logger.info(
            "api_timing %s",
            json.dumps(
                timing.summary(status_code=status_code, total_ms=total_ms),
                separators=(",", ":"),
            ),
        )
