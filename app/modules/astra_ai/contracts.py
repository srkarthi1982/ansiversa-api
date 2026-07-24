from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssistantIntentType(StrEnum):
    PLATFORM_INFORMATION = "platform_information"
    APP_DISCOVERY = "app_discovery"
    APP_COMPARISON = "app_comparison"
    CATEGORY_DISCOVERY = "category_discovery"
    NAVIGATION_GUIDANCE = "navigation_guidance"
    ACCOUNT_GUIDANCE = "account_guidance"
    PRICING_SUBSCRIPTION_GUIDANCE = "pricing_subscription_guidance"
    LEGAL_POLICY_GUIDANCE = "legal_policy_guidance"
    HELP_FAQ = "help_faq"
    CAPABILITY_CLARIFICATION = "capability_clarification"
    UNSUPPORTED_REQUEST = "unsupported_request"
    FUTURE_APP_ACTION_REQUEST = "future_app_action_request"


class PolicyDecisionType(StrEnum):
    ALLOW_READ_ONLY = "allow_read_only"
    CLARIFY = "clarify"
    REFUSE = "refuse"
    PROPOSE_ACTION_ONLY = "propose_action_only"


class RefusalReason(StrEnum):
    PRIVATE_DATA_ACCESS = "private_data_access"
    CROSS_USER_ACCESS = "cross_user_access"
    UNSUPPORTED_SCOPE = "unsupported_scope"
    PROMPT_CONFLICT = "prompt_conflict"
    UNAUTHORIZED = "unauthorized"
    AMBIGUOUS = "ambiguous"
    SECRET_OR_INTERNAL_ACCESS = "secret_or_internal_access"


class ExecutionStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PROPOSED_NOT_EXECUTED = "proposed_not_executed"
    BLOCKED_BY_POLICY = "blocked_by_policy"


class ResponseClassification(StrEnum):
    PLATFORM_GUIDANCE = "platform_guidance"
    CLARIFICATION = "clarification"
    REFUSAL = "refusal"
    ACTION_PROPOSAL = "action_proposal"


class AuthenticatedUserContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_authenticated: bool = False
    user_reference: str | None = Field(default=None, max_length=120)
    permission_scopes: tuple[str, ...] = Field(default_factory=tuple, max_length=20)

    @field_validator("user_reference")
    @classmethod
    def require_reference_for_authenticated_users(cls, value: str | None, info):
        if info.data.get("is_authenticated") and not value:
            raise ValueError("Authenticated context requires a bounded user reference.")
        return value


class ConversationContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str | None = Field(default=None, max_length=120)
    current_route: str | None = Field(default=None, max_length=240)
    previous_intent: AssistantIntentType | None = None
    turn_count: int = Field(default=0, ge=0, le=100)


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=1000)
    user_context: AuthenticatedUserContext = Field(default_factory=AuthenticatedUserContext)
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("Message is required.")
        return message


class PlatformAppSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    name: str
    category: str
    overview_route: str
    explore_route: str
    capabilities: tuple[str, ...] = Field(default_factory=tuple, max_length=12)


class PlatformRouteSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: str
    label: str
    public: bool


class PlatformContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    apps: tuple[PlatformAppSummary, ...] = Field(default_factory=tuple, max_length=100)
    categories: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    routes: tuple[PlatformRouteSummary, ...] = Field(default_factory=tuple, max_length=220)
    documentation_sources: tuple[str, ...] = Field(default_factory=tuple, max_length=40)
    knowledge_sources: tuple[str, ...] = Field(default_factory=tuple, max_length=40)
    authentication_state: str
    authorization_boundary: str


class AssistantIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: AssistantIntentType
    confidence: str = Field(pattern="^(high|medium|low)$")
    matched_terms: tuple[str, ...] = Field(default_factory=tuple, max_length=20)
    clarification_reason: str | None = Field(default=None, max_length=240)


class ClarificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str
    question: str


class RefusalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: RefusalReason
    message: str


class ActionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: str = Field(max_length=80)
    label: str = Field(max_length=120)
    route: str | None = Field(default=None, max_length=240)
    requires_future_authorization: bool = True
    execution_status: ExecutionStatus = ExecutionStatus.PROPOSED_NOT_EXECUTED


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: str


class AuditMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    resolved_intent: AssistantIntentType
    policy_decision: PolicyDecisionType
    authorization_result: str
    context_sources_used: tuple[str, ...] = Field(default_factory=tuple, max_length=40)
    refusal_reason: RefusalReason | None = None
    clarification_reason: str | None = None
    proposed_action_type: str | None = None
    execution_status: ExecutionStatus
    response_classification: ResponseClassification
    runtime_enabled: bool = False
    evidence: tuple[EvidenceItem, ...] = Field(default_factory=tuple, max_length=30)


class AssistantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    classification: ResponseClassification
    intent: AssistantIntent
    policy_decision: PolicyDecisionType
    platform_context: PlatformContext
    clarification: ClarificationRequest | None = None
    refusal: RefusalResponse | None = None
    action_proposal: ActionProposal | None = None
    audit: AuditMetadata
