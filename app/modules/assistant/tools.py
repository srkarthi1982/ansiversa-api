from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Literal

from app.modules.assistant.schemas import AssistantAction
from app.modules.auth.models import User


LOGGER = logging.getLogger(__name__)
ToolVisibility = Literal["public", "authenticated", "internal"]
ToolStatus = Literal["success", "empty", "denied", "invalid_request", "timeout", "unavailable", "error"]
AuditOutcome = Literal["allowed", "denied", "failed", "unavailable"]
MAX_TOOL_ARGUMENT_CHARS = 2000
MAX_TOOL_DATA_CHARS = 5000
MAX_TOOL_SUMMARY_FACTS = 8
MAX_TOOL_ACTIONS = 3
UNSAFE_ARGUMENT_PATTERN = re.compile(
    r"(--|;|/\*|\*/|\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b|\balter\b|\bunion\b|\.\./|//)",
    re.IGNORECASE,
)


class AssistantToolError(Exception):
    status: ToolStatus = "error"
    user_message = "Tool execution failed."


class AssistantToolAuthenticationError(AssistantToolError):
    status: ToolStatus = "denied"
    user_message = "Authentication is required."


class AssistantToolValidationError(AssistantToolError):
    status: ToolStatus = "invalid_request"
    user_message = "Tool request is invalid."


class AssistantToolNotFoundError(AssistantToolError):
    status: ToolStatus = "unavailable"
    user_message = "Tool is unavailable."


class AssistantToolTimeoutError(AssistantToolError):
    status: ToolStatus = "timeout"
    user_message = "Tool execution timed out."


@dataclass(frozen=True)
class AssistantToolContext:
    request_id: str
    user: User | None = None
    current_route: str | None = None
    current_app_slug: str | None = None
    allowed_routes: frozenset[str] = field(default_factory=frozenset)
    max_tool_calls: int = 1

    @property
    def user_id(self) -> str | None:
        return self.user.id if self.user else None


@dataclass(frozen=True)
class AssistantToolAuditMetadata:
    request_id: str
    tool_name: str
    source_app: str
    outcome: AuditOutcome
    status: ToolStatus
    duration_ms: int
    result_count: int = 0
    response_mode: str = "deterministic"
    fallback_reason: str | None = None

    def as_log_metadata(self) -> dict[str, object]:
        metadata: dict[str, object] = {
            "requestId": self.request_id,
            "toolName": self.tool_name,
            "sourceApp": self.source_app,
            "outcome": self.outcome,
            "status": self.status,
            "durationMs": self.duration_ms,
            "resultCount": self.result_count,
            "responseMode": self.response_mode,
        }
        if self.fallback_reason:
            metadata["fallbackReason"] = self.fallback_reason
        return metadata


@dataclass(frozen=True)
class AssistantToolResult:
    tool_name: str
    source_app: str
    status: ToolStatus
    data: dict[str, Any] = field(default_factory=dict)
    summary_facts: tuple[str, ...] = ()
    actions: tuple[AssistantAction, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def result_count(self) -> int:
        value = self.metadata.get("resultCount")
        if isinstance(value, int):
            return max(0, value)
        for key in ("items", "favorites", "results"):
            candidate = self.data.get(key)
            if isinstance(candidate, list):
                return len(candidate)
        return 0


ToolHandler = Callable[[AssistantToolContext, dict[str, Any]], AssistantToolResult]


@dataclass(frozen=True)
class AssistantToolDefinition:
    name: str
    description: str
    source_app: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    handler: ToolHandler
    requires_authentication: bool = True
    read_only: bool = True
    timeout_seconds: float = 2.0
    visibility: ToolVisibility = "authenticated"
    deterministic_intents: tuple[str, ...] = ()
    max_result_items: int = 10

    def __post_init__(self) -> None:
        if not self.name or not re.fullmatch(r"[a-z][a-z0-9_]{2,120}", self.name):
            raise AssistantToolValidationError("Tool name must be stable snake_case.")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 30:
            raise AssistantToolValidationError("Tool timeout must be between 0 and 30 seconds.")
        if self.max_result_items < 0 or self.max_result_items > 100:
            raise AssistantToolValidationError("Tool result limit must be between 0 and 100.")

    def model_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class AssistantToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, AssistantToolDefinition] = {}
        self._intent_map: dict[str, str] = {}

    def register(self, definition: AssistantToolDefinition) -> None:
        if definition.name in self._tools:
            raise AssistantToolValidationError(f"Duplicate tool name: {definition.name}")
        self._tools[definition.name] = definition
        for intent in definition.deterministic_intents:
            normalized = _normalize_intent(intent)
            existing = self._intent_map.get(normalized)
            if existing and existing != definition.name:
                raise AssistantToolValidationError(f"Duplicate tool intent: {intent}")
            self._intent_map[normalized] = definition.name

    def get(self, name: str) -> AssistantToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise AssistantToolNotFoundError(f"Unknown tool: {name}") from exc

    def list_tools(
        self,
        *,
        authenticated: bool,
        visibility: ToolVisibility | None = None,
        read_only_only: bool = True,
    ) -> tuple[AssistantToolDefinition, ...]:
        tools: list[AssistantToolDefinition] = []
        for definition in self._tools.values():
            if read_only_only and not definition.read_only:
                continue
            if definition.requires_authentication and not authenticated:
                continue
            if visibility is not None and definition.visibility != visibility:
                continue
            if definition.visibility == "internal":
                continue
            tools.append(definition)
        return tuple(sorted(tools, key=lambda tool: tool.name))

    def lookup_intent(self, intent: str) -> AssistantToolDefinition | None:
        tool_name = self._intent_map.get(_normalize_intent(intent))
        return self._tools.get(tool_name) if tool_name else None

    def model_schemas(self, *, authenticated: bool) -> tuple[dict[str, Any], ...]:
        return tuple(
            tool.model_schema()
            for tool in self.list_tools(authenticated=authenticated, read_only_only=True)
        )


class AssistantToolExecutor:
    def __init__(
        self,
        registry: AssistantToolRegistry,
        *,
        max_tool_calls: int = 1,
        phase_read_only_only: bool = True,
    ) -> None:
        self.registry = registry
        self.max_tool_calls = max(1, min(max_tool_calls, 3))
        self.phase_read_only_only = phase_read_only_only

    def execute(
        self,
        tool_name: str,
        arguments: Mapping[str, Any] | None,
        context: AssistantToolContext,
    ) -> AssistantToolResult:
        start = perf_counter()
        definition = self.registry.get(tool_name)
        audit_status: ToolStatus = "success"
        fallback_reason: str | None = None
        try:
            if context.max_tool_calls > self.max_tool_calls:
                raise AssistantToolValidationError("Tool call count exceeds Phase 1 limit.")
            if self.phase_read_only_only and not definition.read_only:
                raise AssistantToolValidationError("Write tools are not allowed in Phase 1.")
            if definition.requires_authentication and context.user is None:
                raise AssistantToolAuthenticationError()

            validated_arguments = validate_tool_arguments(definition.input_schema, arguments or {})
            result = definition.handler(context, validated_arguments)
            duration_ms = int((perf_counter() - start) * 1000)
            if duration_ms > int(definition.timeout_seconds * 1000):
                raise AssistantToolTimeoutError()
            sanitized = sanitize_tool_result(definition, result, context.allowed_routes)
            audit_status = sanitized.status
            self._record_audit(
                AssistantToolAuditMetadata(
                    request_id=context.request_id,
                    tool_name=definition.name,
                    source_app=definition.source_app,
                    outcome="allowed",
                    status=audit_status,
                    duration_ms=duration_ms,
                    result_count=sanitized.result_count,
                )
            )
            return sanitized
        except AssistantToolError as exc:
            duration_ms = int((perf_counter() - start) * 1000)
            audit_status = exc.status
            fallback_reason = exc.user_message
            self._record_audit(
                AssistantToolAuditMetadata(
                    request_id=context.request_id,
                    tool_name=definition.name,
                    source_app=definition.source_app,
                    outcome="denied" if exc.status in {"denied", "invalid_request"} else "unavailable",
                    status=exc.status,
                    duration_ms=duration_ms,
                    fallback_reason=fallback_reason,
                )
            )
            return AssistantToolResult(
                tool_name=definition.name,
                source_app=definition.source_app,
                status=exc.status,
                data={},
                summary_facts=(exc.user_message,),
                actions=(),
                metadata={"fallbackReason": fallback_reason},
            )
        except Exception:
            duration_ms = int((perf_counter() - start) * 1000)
            LOGGER.exception("Astra tool execution failed for %s.", definition.name)
            self._record_audit(
                AssistantToolAuditMetadata(
                    request_id=context.request_id,
                    tool_name=definition.name,
                    source_app=definition.source_app,
                    outcome="failed",
                    status="error",
                    duration_ms=duration_ms,
                    fallback_reason="handler_exception",
                )
            )
            return AssistantToolResult(
                tool_name=definition.name,
                source_app=definition.source_app,
                status="error",
                data={},
                summary_facts=("Tool result is temporarily unavailable.",),
                actions=(),
                metadata={"fallbackReason": "handler_exception"},
            )

    def _record_audit(self, metadata: AssistantToolAuditMetadata) -> None:
        LOGGER.info("Astra tool audit metadata: %s", metadata.as_log_metadata())


def validate_tool_arguments(
    schema: Mapping[str, Any],
    arguments: Mapping[str, Any],
) -> dict[str, Any]:
    _ensure_json_size(arguments, MAX_TOOL_ARGUMENT_CHARS, "Tool arguments are too large.")
    if not isinstance(arguments, Mapping):
        raise AssistantToolValidationError("Tool arguments must be an object.")
    if schema.get("type") not in (None, "object"):
        raise AssistantToolValidationError("Tool input schema must be an object.")

    required = set(schema.get("required") or ())
    properties = schema.get("properties") or {}
    if not isinstance(properties, Mapping):
        raise AssistantToolValidationError("Tool input schema properties are invalid.")
    allowed_keys = set(properties)
    extra_keys = set(arguments) - allowed_keys
    if schema.get("additionalProperties") is False and extra_keys:
        raise AssistantToolValidationError("Unknown tool argument.")
    missing = required - set(arguments)
    if missing:
        raise AssistantToolValidationError("Required tool argument is missing.")

    validated: dict[str, Any] = {}
    for key, value in arguments.items():
        if key not in properties:
            continue
        if key in {"user_id", "userId", "owner_id", "ownerId", "tenant_id", "tenantId"}:
            raise AssistantToolValidationError("Caller-controlled identity arguments are forbidden.")
        validated[key] = _validate_schema_value(str(key), value, properties[key])
    return validated


def sanitize_tool_result(
    definition: AssistantToolDefinition,
    result: AssistantToolResult,
    allowed_routes: frozenset[str],
) -> AssistantToolResult:
    if result.tool_name != definition.name or result.source_app != definition.source_app:
        raise AssistantToolValidationError("Tool result identity mismatch.")
    validate_tool_output(definition.output_schema, result.data)
    _ensure_json_size(result.data, MAX_TOOL_DATA_CHARS, "Tool result is too large.")
    summary_facts = tuple(_safe_text(value, max_length=240) for value in result.summary_facts[:MAX_TOOL_SUMMARY_FACTS])
    actions = tuple(_sanitize_actions(result.actions, allowed_routes))
    metadata = _sanitize_metadata(result.metadata)
    if result.result_count > definition.max_result_items:
        raise AssistantToolValidationError("Tool result count exceeds the approved limit.")
    return AssistantToolResult(
        tool_name=result.tool_name,
        source_app=result.source_app,
        status=result.status,
        data=result.data,
        summary_facts=summary_facts,
        actions=actions,
        metadata=metadata,
    )


def validate_tool_output(schema: Mapping[str, Any], data: Mapping[str, Any]) -> None:
    if not isinstance(data, Mapping):
        raise AssistantToolValidationError("Tool result data must be an object.")
    if schema.get("type") not in (None, "object"):
        raise AssistantToolValidationError("Tool output schema must be an object.")

    required = set(schema.get("required") or ())
    properties = schema.get("properties") or {}
    if not isinstance(properties, Mapping):
        raise AssistantToolValidationError("Tool output schema properties are invalid.")
    missing = required - set(data)
    if missing:
        raise AssistantToolValidationError("Tool result is missing required fields.")
    if schema.get("additionalProperties") is False:
        extra = set(data) - set(properties)
        if extra:
            raise AssistantToolValidationError("Tool result contains unapproved fields.")

    for key, value in data.items():
        property_schema = properties.get(key)
        if property_schema is None:
            continue
        _validate_output_value(value, property_schema)


def _validate_output_value(value: Any, schema: Any) -> None:
    if not isinstance(schema, Mapping):
        raise AssistantToolValidationError("Tool output schema is invalid.")
    expected_type = schema.get("type")
    if expected_type == "string" and not isinstance(value, str):
        raise AssistantToolValidationError("Tool result field type is invalid.")
    if expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise AssistantToolValidationError("Tool result field type is invalid.")
    if expected_type == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
        raise AssistantToolValidationError("Tool result field type is invalid.")
    if expected_type == "boolean" and not isinstance(value, bool):
        raise AssistantToolValidationError("Tool result field type is invalid.")
    if expected_type == "array" and not isinstance(value, list):
        raise AssistantToolValidationError("Tool result field type is invalid.")
    if expected_type == "object" and not isinstance(value, Mapping):
        raise AssistantToolValidationError("Tool result field type is invalid.")


def _normalize_intent(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def _ensure_json_size(value: object, max_chars: int, message: str) -> None:
    try:
        encoded = json.dumps(value, default=str, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise AssistantToolValidationError("Tool payload must be JSON serializable.") from exc
    if len(encoded) > max_chars:
        raise AssistantToolValidationError(message)


def _validate_schema_value(key: str, value: Any, schema: Any) -> Any:
    if not isinstance(schema, Mapping):
        raise AssistantToolValidationError("Tool input schema is invalid.")
    expected_type = schema.get("type")
    if expected_type == "string":
        if not isinstance(value, str):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        max_length = int(schema.get("maxLength") or 240)
        text = _safe_text(value, max_length=max_length)
        if UNSAFE_ARGUMENT_PATTERN.search(text):
            raise AssistantToolValidationError("Tool argument contains unsupported content.")
        return text
    if expected_type == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and value < int(minimum):
            raise AssistantToolValidationError("Tool argument is below the allowed range.")
        if maximum is not None and value > int(maximum):
            raise AssistantToolValidationError("Tool argument exceeds the allowed range.")
        return value
    if expected_type == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        return value
    if expected_type == "boolean":
        if not isinstance(value, bool):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        return value
    if expected_type == "array":
        if not isinstance(value, list):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        max_items = int(schema.get("maxItems") or 10)
        if len(value) > max_items:
            raise AssistantToolValidationError("Tool argument list is too large.")
        item_schema = schema.get("items") or {}
        return [_validate_schema_value(key, item, item_schema) for item in value]
    if expected_type == "object":
        if not isinstance(value, Mapping):
            raise AssistantToolValidationError("Tool argument type is invalid.")
        return validate_tool_arguments(schema, value)
    raise AssistantToolValidationError("Tool argument schema type is unsupported.")


def _safe_text(value: str, *, max_length: int) -> str:
    text = " ".join(value.strip().split())
    if len(text) > max_length:
        raise AssistantToolValidationError("Tool text field is too large.")
    if UNSAFE_ARGUMENT_PATTERN.search(text):
        raise AssistantToolValidationError("Tool text field contains unsupported content.")
    return text


def _sanitize_actions(
    actions: tuple[AssistantAction, ...],
    allowed_routes: frozenset[str],
) -> list[AssistantAction]:
    sanitized: list[AssistantAction] = []
    seen_routes: set[str] = set()
    for action in actions:
        if action.route not in allowed_routes or action.route in seen_routes:
            continue
        sanitized.append(action)
        seen_routes.add(action.route)
        if len(sanitized) == MAX_TOOL_ACTIONS:
            break
    return sanitized


def _sanitize_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in metadata.items():
        if key.lower() in {"sql", "token", "secret", "password", "rawrecord", "raw_record"}:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
    _ensure_json_size(safe, 1000, "Tool metadata is too large.")
    return safe
