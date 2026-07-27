from __future__ import annotations

import inspect
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

import app.modules.astra_ai.planning as planning_module
from app.modules.astra_ai.capability_discovery import (
    AstraCapabilityDiscoveryEngine,
    AstraCapabilityExecutionAuthority,
    AstraCapabilityMetadata,
    AstraCapabilityStatus,
    AstraCapabilityType,
    AstraCapabilityVisibility,
)
from app.modules.astra_ai.constitutional_contracts import (
    ApprovalState,
    AuthorityClass,
    ConstitutionalRequirementReference,
    GovernanceOutcome,
    ProductionAuthorizationState,
    SafetyClassification,
)
from app.modules.astra_ai.conversation_context import (
    AstraConversationContextEngine,
    AstraConversationLifecycleState,
    AstraConversationMetadata,
    AstraConversationSnapshot,
)
from app.modules.astra_ai.planning import (
    AstraExecutionAuthorizationState,
    AstraPlanStatus,
    AstraPlanningEngine,
    AstraPlanningError,
    AstraPlanningRequest,
    AstraRequestedCompletionPosture,
    AstraRequestedPlanStep,
)
from app.modules.astra_ai.runtime import AstraRuntime, AstraRuntimeComponentIdentifier, AstraRuntimeError


NOW = datetime(2026, 7, 27, 6, 0, tzinfo=timezone.utc)
INSTANCE = "astra_rt_" + "8" * 32


def requirement():
    return ConstitutionalRequirementReference(
        constitutional_source="ASTRA-005",
        requirement_id="AIR-PLN-001",
        requirement_version="1.0.0",
    )


def ready_runtime(suffix="8", capacity=1000):
    runtime = AstraRuntime(
        created_at=NOW,
        startup_instance_id="astra_rt_" + suffix * 32,
        evidence_sink_capacity=capacity,
    )
    runtime.startup()
    return runtime


def allow_governance(runtime):
    original = runtime.evaluate_governance

    def evaluate(contract):
        result = original(contract)
        return result.model_copy(update={"decision": result.decision.model_copy(update={"outcome": GovernanceOutcome.ALLOW})})

    runtime.evaluate_governance = evaluate


def conversation(runtime, conversation_id="conv_planning_0001"):
    engine = AstraConversationContextEngine(runtime=runtime)
    snapshot = engine.create_conversation(conversation_id=conversation_id, created_at=NOW)
    return engine, snapshot


def step(
    number=1,
    capability_id="cap_conversation_context_0001",
    dependencies=(),
    step_id=None,
):
    return AstraRequestedPlanStep(
        step_id=step_id or f"step_planning_{number:04d}",
        sequence_number=number,
        capability_id=capability_id,
        objective_reference=f"objective:planning:{number}",
        dependency_step_ids=dependencies,
    )


def request(runtime, snapshot, steps=None, maximum=5):
    return AstraPlanningRequest(
        planning_request_id="planning_req_planning_0001",
        runtime_instance_id=runtime.identity.startup_instance_id,
        conversation_id=snapshot.metadata.conversation_id,
        request_reference="request:planning:0001",
        objective_reference="objective:planning:root",
        requester_context_reference="requester:runtime:internal",
        constitutional_requirement_references=(requirement(),),
        maximum_step_count=maximum,
        requested_steps=steps or (step(),),
        requested_completion_posture=AstraRequestedCompletionPosture.PROPOSAL_ONLY,
        planning_timestamp=NOW,
        planning_version="1.0.0",
    )


def propose(runtime, engine, snapshot, planning_request):
    return runtime.planning.propose(
        planning_request,
        conversation_engine=engine,
        conversation_snapshot=snapshot,
        requester_context=runtime.capability_discovery.internal_request_context(),
    )


def test_runtime_registers_exactly_one_planning_engine():
    runtime = ready_runtime()
    registrations = [
        item for item in runtime.component_registrations if item.component_identifier is AstraRuntimeComponentIdentifier.PLANNING
    ]
    assert len(registrations) == 1
    assert registrations[0].implementation_reference == "ASTRA-IMP-008"


def test_planning_requires_ready_runtime_and_handle_expires_after_shutdown():
    runtime = AstraRuntime(created_at=NOW, startup_instance_id=INSTANCE)
    engine = AstraPlanningEngine(runtime=runtime)
    with pytest.raises(AstraPlanningError):
        engine.propose(object(), conversation_engine=object(), conversation_snapshot=object(), requester_context=object())

    runtime.startup()
    interface = runtime.planning
    context = runtime.capability_discovery.internal_request_context()
    conv_engine, snapshot = conversation(runtime)
    planning_request = request(runtime, snapshot)
    runtime.shutdown()
    with pytest.raises(AstraRuntimeError):
        interface.propose(
            planning_request,
            conversation_engine=conv_engine,
            conversation_snapshot=snapshot,
            requester_context=context,
        )


def test_default_governance_blocks_and_releases_no_steps():
    runtime = ready_runtime()
    engine, snapshot = conversation(runtime)
    plan = propose(runtime, engine, snapshot, request(runtime, snapshot))
    assert plan.plan_status is AstraPlanStatus.GOVERNANCE_BLOCKED
    assert plan.proposed_steps == ()


@pytest.mark.parametrize(
    ("outcome", "status"),
    (
        (GovernanceOutcome.CLARIFY, AstraPlanStatus.CLARIFICATION_REQUIRED),
        (GovernanceOutcome.DEFER, AstraPlanStatus.DEFERRED),
        (GovernanceOutcome.REFUSE, AstraPlanStatus.REFUSED),
        (GovernanceOutcome.CONTAIN, AstraPlanStatus.CONTAINED),
        (GovernanceOutcome.FAIL_CLOSED, AstraPlanStatus.GOVERNANCE_BLOCKED),
    ),
)
def test_non_allow_outcomes_map_without_actionable_steps(outcome, status):
    runtime = ready_runtime("7")
    original = runtime.evaluate_governance

    def forced(contract):
        result = original(contract)
        return result.model_copy(update={"decision": result.decision.model_copy(update={"outcome": outcome})})

    runtime.evaluate_governance = forced
    engine, snapshot = conversation(runtime)
    plan = propose(runtime, engine, snapshot, request(runtime, snapshot))
    assert plan.plan_status is status
    assert plan.proposed_steps == ()


def test_allowed_plan_is_deterministic_immutable_and_never_authorized():
    runtime = ready_runtime()
    allow_governance(runtime)
    engine, snapshot = conversation(runtime)
    planning_request = request(runtime, snapshot)
    first = propose(runtime, engine, snapshot, planning_request)
    second = propose(runtime, engine, snapshot, planning_request)
    assert first.plan_id == second.plan_id
    assert first.proposed_steps == second.proposed_steps
    assert first.execution_authorization_state is AstraExecutionAuthorizationState.NOT_AUTHORIZED
    assert first.production_authorization_state is ProductionAuthorizationState.NOT_APPROVED
    with pytest.raises(ValidationError):
        first.plan_status = AstraPlanStatus.INVALID


def test_owner_issued_requester_authority_is_required():
    runtime = ready_runtime()
    allow_governance(runtime)
    engine, snapshot = conversation(runtime)
    forged = runtime.capability_discovery.internal_request_context().model_copy(update={"authority_token": object()})
    with pytest.raises(Exception):
        runtime.planning.propose(
            request(runtime, snapshot),
            conversation_engine=engine,
            conversation_snapshot=snapshot,
            requester_context=forged,
        )


def test_fabricated_stale_foreign_and_closed_conversations_are_rejected():
    runtime = ready_runtime()
    allow_governance(runtime)
    engine, snapshot = conversation(runtime)
    forged = AstraConversationSnapshot(
        metadata=AstraConversationMetadata(
            conversation_id="conv_forged_0001",
            runtime_instance_id=runtime.identity.startup_instance_id,
            created_at=NOW,
            last_activity_at=NOW,
            conversation_version="1.0.0",
            implementation_reference="ASTRA-IMP-006",
            lifecycle_state=AstraConversationLifecycleState.ACTIVE,
        )
    )
    with pytest.raises(AstraPlanningError):
        propose(runtime, engine, forged, request(runtime, forged))

    engine.transition_conversation(
        snapshot.metadata.conversation_id,
        AstraConversationLifecycleState.ACTIVE,
        transitioned_at=NOW,
        summary_reference="conversation:active",
        entry_id="ctx_planning_transition_0001",
    )
    with pytest.raises(AstraPlanningError):
        propose(runtime, engine, snapshot, request(runtime, snapshot))

    foreign = ready_runtime("6")
    allow_governance(foreign)
    with pytest.raises(AstraPlanningError):
        foreign.planning.propose(
            request(runtime, engine.get_conversation(snapshot.metadata.conversation_id)),
            conversation_engine=engine,
            conversation_snapshot=engine.get_conversation(snapshot.metadata.conversation_id),
            requester_context=foreign.capability_discovery.internal_request_context(),
        )


@pytest.mark.parametrize(
    "steps",
    (
        (step(2),),
        (step(1, dependencies=("step_planning_0001",)),),
        (step(1), step(2, dependencies=("step_planning_0002",))),
        (step(1), step(2, dependencies=("step_planning_0001", "step_planning_0001"))),
        (step(1), step(2, dependencies=("step_missing_0001",))),
        (step(1), step(1, capability_id="cap_evidence_metadata_0001")),
    ),
)
def test_invalid_dependency_and_sequence_graphs_fail_before_planning_evidence(steps):
    runtime = ready_runtime()
    engine, snapshot = conversation(runtime)
    planning_request = request(runtime, snapshot, steps=steps)
    before = runtime.evidence_count()
    with pytest.raises(AstraPlanningError):
        propose(runtime, engine, snapshot, planning_request)
    assert runtime.evidence_count() == before


def test_maximum_step_count_is_enforced_by_contract():
    runtime = ready_runtime()
    engine, snapshot = conversation(runtime)
    with pytest.raises((ValidationError, AstraPlanningError)):
        request(runtime, snapshot, steps=(step(1), step(2, capability_id="cap_evidence_metadata_0001")), maximum=1)


def test_unknown_and_duplicate_capabilities_are_rejected():
    runtime = ready_runtime()
    allow_governance(runtime)
    engine, snapshot = conversation(runtime)
    with pytest.raises(AstraPlanningError):
        propose(runtime, engine, snapshot, request(runtime, snapshot, steps=(step(capability_id="cap_unknown_0001"),)))
    with pytest.raises(AstraPlanningError):
        propose(runtime, engine, snapshot, request(runtime, snapshot, steps=(step(1), step(2))))


def test_disabled_and_deprecated_capabilities_are_ineligible_by_default():
    for status, suffix in ((AstraCapabilityStatus.DISABLED, "4"), (AstraCapabilityStatus.DEPRECATED, "3")):
        runtime = ready_runtime(suffix)
        allow_governance(runtime)
        metadata = AstraCapabilityMetadata(
            capability_id="cap_ineligible_0001",
            capability_name="Ineligible Planning Metadata",
            capability_type=AstraCapabilityType.PLATFORM_METADATA,
            owning_module="app.modules.astra_ai.planning",
            version="1.0.0",
            status=status,
            visibility=AstraCapabilityVisibility.INTERNAL,
            governance_reference=requirement(),
            execution_authority=AstraCapabilityExecutionAuthority.METADATA_ONLY,
            description="Metadata-only ineligible planning test capability.",
        )
        runtime._capability_discovery = AstraCapabilityDiscoveryEngine(runtime=runtime, capabilities=(metadata,))
        engine, snapshot = conversation(runtime)
        with pytest.raises(AstraPlanningError):
            propose(runtime, engine, snapshot, request(runtime, snapshot, steps=(step(capability_id=metadata.capability_id),)))


def test_evidence_failure_releases_no_plan_and_does_not_advance_sequence():
    runtime = ready_runtime(capacity=2)
    engine, snapshot = conversation(runtime)  # consumes one record
    before_sequence = runtime._planning._operation_sequence
    with pytest.raises(Exception):
        propose(runtime, engine, snapshot, request(runtime, snapshot))  # discovery consumes final record
    assert runtime._planning._operation_sequence == before_sequence


def test_success_emits_one_planning_record_and_does_not_mutate_dependencies():
    runtime = ready_runtime()
    allow_governance(runtime)
    engine, snapshot = conversation(runtime)
    registry_before = runtime._capability_discovery.registry
    conversation_before = engine.get_conversation(snapshot.metadata.conversation_id)
    before = runtime.evidence_count()
    plan = propose(runtime, engine, snapshot, request(runtime, snapshot))
    added = runtime.retrieve_evidence()[before:]
    planning_records = [item for item in added if item.integrity.source_system == "astra_ai:planning"]
    assert len(planning_records) == 1
    assert plan.evidence_references[-1] == planning_records[0].evidence_id
    assert engine.get_conversation(snapshot.metadata.conversation_id) == conversation_before
    assert runtime._capability_discovery.registry.capability_count == registry_before.capability_count


def test_contracts_and_source_have_no_executable_or_provider_surface():
    dumped = request(ready_runtime(), AstraConversationSnapshot(
        metadata=AstraConversationMetadata(
            conversation_id="conv_contract_0001",
            runtime_instance_id=INSTANCE,
            created_at=NOW,
            last_activity_at=NOW,
            conversation_version="1.0.0",
            implementation_reference="ASTRA-IMP-006",
            lifecycle_state=AstraConversationLifecycleState.CREATED,
        )
    )).model_dump()
    assert not {"handler", "callable", "command", "sql", "prompt", "provider_payload"} & set(dumped)
    source = inspect.getsource(planning_module).lower()
    for forbidden in ("from fastapi", "sqlalchemy", "import openai", "httpx", "requests.", "subprocess"):
        assert forbidden not in source
