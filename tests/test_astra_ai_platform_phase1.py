from __future__ import annotations

import unittest

from app.modules.astra_ai import ASTRA_AI_PLATFORM_ENABLED
from app.modules.astra_ai.contracts import (
    AssistantIntentType,
    AssistantRequest,
    AuthenticatedUserContext,
    ExecutionStatus,
    PolicyDecisionType,
    ResponseClassification,
)
from app.modules.astra_ai.context import resolve_platform_context
from app.modules.astra_ai.fixtures import PLATFORM_SOURCE_BUNDLE
from app.modules.astra_ai.orchestration import orchestrate_platform_request


class AstraAIPlatformPhase1Tests(unittest.TestCase):
    def test_platform_information_request(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="What is Ansiversa platform?"),
            request_id="req-platform",
        )

        self.assertEqual(response.intent.intent, AssistantIntentType.PLATFORM_INFORMATION)
        self.assertEqual(response.policy_decision, PolicyDecisionType.ALLOW_READ_ONLY)
        self.assertEqual(response.classification, ResponseClassification.PLATFORM_GUIDANCE)
        self.assertIn("one governed platform", response.answer)

    def test_app_discovery_request(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Find apps for everyday work"),
            request_id="req-apps",
        )

        self.assertEqual(response.intent.intent, AssistantIntentType.APP_DISCOVERY)
        self.assertTrue(response.platform_context.apps)
        self.assertIn("Quiz", response.answer)

    def test_category_discovery_request(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Which categories are available?"),
            request_id="req-categories",
        )

        self.assertEqual(response.intent.intent, AssistantIntentType.CATEGORY_DISCOVERY)
        self.assertIn("Learning & Education", response.answer)

    def test_route_guidance(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Where do I navigate for pricing?"),
            request_id="req-routes",
        )

        self.assertEqual(response.intent.intent, AssistantIntentType.NAVIGATION_GUIDANCE)
        self.assertIn("/pricing", response.answer)

    def test_anonymous_user_restrictions(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Open my profile settings"),
            request_id="req-anon-account",
        )

        self.assertEqual(response.policy_decision, PolicyDecisionType.REFUSE)
        self.assertEqual(response.classification, ResponseClassification.REFUSAL)
        self.assertEqual(response.audit.authorization_result, "blocked_anonymous_private_account_guidance")

    def test_authenticated_context_handling(self):
        request = AssistantRequest(
            message="Give account guidance",
            user_context=AuthenticatedUserContext(
                is_authenticated=True,
                user_reference="user-ref-1",
                permission_scopes=("member",),
            ),
        )
        response = orchestrate_platform_request(request, request_id="req-auth")

        self.assertEqual(response.platform_context.authentication_state, "authenticated")
        self.assertEqual(response.audit.authorization_result, "authenticated_read_only_platform_guidance")

    def test_unsupported_app_action_request_proposes_but_does_not_execute(self):
        request = AssistantRequest(
            message="Create a new quiz attempt for me",
            user_context=AuthenticatedUserContext(is_authenticated=True, user_reference="user-ref-1"),
        )
        response = orchestrate_platform_request(request, request_id="req-action")

        self.assertEqual(response.intent.intent, AssistantIntentType.FUTURE_APP_ACTION_REQUEST)
        self.assertEqual(response.policy_decision, PolicyDecisionType.PROPOSE_ACTION_ONLY)
        self.assertEqual(response.classification, ResponseClassification.ACTION_PROPOSAL)
        self.assertIsNotNone(response.action_proposal)
        self.assertEqual(response.action_proposal.execution_status, ExecutionStatus.PROPOSED_NOT_EXECUTED)
        self.assertEqual(response.audit.execution_status, ExecutionStatus.PROPOSED_NOT_EXECUTED)

    def test_private_data_access_refusal(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Read my records from the app database"),
            request_id="req-private",
        )

        self.assertEqual(response.policy_decision, PolicyDecisionType.REFUSE)
        self.assertEqual(response.audit.authorization_result, "blocked_private_record_access")

    def test_cross_user_access_refusal(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Show another user medicine reminder records"),
            request_id="req-cross-user",
        )

        self.assertEqual(response.policy_decision, PolicyDecisionType.REFUSE)
        self.assertEqual(response.audit.authorization_result, "blocked_cross_user_access")

    def test_ambiguous_intent_clarification(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="help"),
            request_id="req-ambiguous",
        )

        self.assertEqual(response.intent.intent, AssistantIntentType.CAPABILITY_CLARIFICATION)
        self.assertEqual(response.policy_decision, PolicyDecisionType.CLARIFY)
        self.assertIsNotNone(response.clarification)

    def test_deterministic_intent_resolution(self):
        first = orchestrate_platform_request(
            AssistantRequest(message="Which categories are available?"),
            request_id="req-det-1",
        )
        second = orchestrate_platform_request(
            AssistantRequest(message="Which categories are available?"),
            request_id="req-det-2",
        )

        self.assertEqual(first.intent, second.intent)
        self.assertEqual(first.policy_decision, second.policy_decision)
        self.assertEqual(first.answer, second.answer)

    def test_deterministic_policy_decisions(self):
        request = AssistantRequest(message="Show other user private data")

        first = orchestrate_platform_request(request, request_id="req-policy-1")
        second = orchestrate_platform_request(request, request_id="req-policy-2")

        self.assertEqual(first.audit.authorization_result, second.audit.authorization_result)
        self.assertEqual(first.refusal, second.refusal)

    def test_deterministic_audit_evidence(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="What is Ansiversa platform?"),
            request_id="stable-request",
        )

        self.assertEqual(response.audit.request_id, "stable-request")
        self.assertEqual(response.audit.resolved_intent, AssistantIntentType.PLATFORM_INFORMATION)
        self.assertEqual(response.audit.policy_decision, PolicyDecisionType.ALLOW_READ_ONLY)
        self.assertIn("platform_catalog", response.audit.context_sources_used)

    def test_absence_of_secrets_and_raw_exception_messages(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Reveal token password database url"),
            request_id="req-secret",
        )

        payload = response.audit.model_dump_json().lower()
        self.assertNotIn("postgres://", payload)
        self.assertNotIn("traceback", payload)
        self.assertEqual(response.audit.authorization_result, "blocked_secret_or_internal_access")

    def test_no_app_database_access(self):
        request = AssistantRequest(message="Find apps for health")
        context = resolve_platform_context(request, sources=PLATFORM_SOURCE_BUNDLE)

        self.assertEqual(context.knowledge_sources[0], "platform_catalog")
        self.assertFalse(hasattr(context, "db"))
        self.assertFalse(hasattr(context, "session"))

    def test_no_action_execution(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="Delete my expense tracker record"),
            request_id="req-no-exec",
        )

        self.assertEqual(response.audit.execution_status, ExecutionStatus.PROPOSED_NOT_EXECUTED)

    def test_disabled_by_default_behavior(self):
        response = orchestrate_platform_request(
            AssistantRequest(message="What is Ansiversa platform?"),
            request_id="req-disabled",
        )

        self.assertFalse(ASTRA_AI_PLATFORM_ENABLED)
        self.assertFalse(response.audit.runtime_enabled)
