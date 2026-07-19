import unittest

from pydantic import ValidationError

from app.modules.assistant.openai_provider import OpenAIProviderError
from app.modules.assistant.schemas import AssistantAction, AssistantQueryRequest
from app.modules.assistant.service import (
    AssistantKnowledgeIndex,
    KnowledgeEntry,
    query_index,
)


def app(slug, name, description, category, aliases=()):
    return KnowledgeEntry(
        id=f"app:{slug}",
        title=name,
        source_type="app",
        route=f"/{slug}",
        summary=description,
        category=category,
        aliases=aliases,
        keywords=(slug.replace("-", " "), category),
        action_label=f"Open {name}",
        action_type="app",
        rank_weight=5,
    )


def page(key, title, route, summary, aliases=(), source_type="platform"):
    return KnowledgeEntry(
        id=f"{source_type}:{key}",
        title=title,
        source_type=source_type,
        route=route,
        summary=summary,
        aliases=aliases,
        keywords=(key, title),
        action_label=f"Open {title}",
        action_type=source_type if source_type != "faq" else "platform",
        rank_weight=3,
    )


class FakeProvider:
    def __init__(self, answer="Grounded answer from approved context.", error=None):
        self.answer = answer
        self.error = error
        self.calls = []

    def generate_answer(self, question, context):
        self.calls.append({"question": question, "context": context})
        if self.error:
            raise self.error
        return self.answer


class AssistantServiceTests(unittest.TestCase):
    def setUp(self):
        self.index = AssistantKnowledgeIndex(
            entries=(
                app(
                    "document-expiry-tracker",
                    "Document Expiry Tracker",
                    "Track passport, ID, licence, permit, insurance, certificate, and other personal document expiry dates.",
                    "Documents & Records",
                    ("passport", "expiry dates"),
                ),
                app(
                    "salary-breakdown-calculator",
                    "Salary Breakdown Calculator",
                    "Compare salary scenarios, recurring earnings, recurring deductions, gross pay, and net salary.",
                    "Finance",
                    ("salary", "net pay"),
                ),
                app(
                    "net-worth-tracker",
                    "Net Worth Tracker",
                    "Track assets, liabilities, snapshots, and currency-separated net worth.",
                    "Finance",
                    ("net worth", "assets"),
                ),
                app(
                    "savings-goal-planner",
                    "Savings Goal Planner",
                    "Track savings goals, milestones, contributions, and remaining balances.",
                    "Finance",
                    ("saving goal", "savings"),
                ),
                page("about", "About", "/about", "About explains the Ansiversa story.", ("what is ansiversa",)),
                page("pricing", "Pricing", "/pricing", "Pricing explains plans and access.", ("price", "plans")),
                page("faq", "FAQ", "/faq", "FAQ answers common platform questions.", ("frequently asked", "help")),
                page("contact", "Contact", "/contact", "Contact is for support.", ("support",)),
                page("privacy", "Privacy Policy", "/privacy", "Privacy explains data-use rules.", ("privacy",), "legal"),
                page("terms", "Terms of Service", "/terms", "Terms explains usage rules.", ("terms",), "legal"),
                KnowledgeEntry(
                    id="internal:agents",
                    title="AGENTS",
                    source_type="platform",
                    route="/internal",
                    summary="Secrets and operational instructions.",
                    keywords=("agents", "credentials", "secrets"),
                    action_label="Open Internal",
                    action_type="platform",
                    visibility="internal",
                ),
                KnowledgeEntry(
                    id="platform:broken",
                    title="Broken Route",
                    source_type="platform",
                    route="/not-allowed",
                    summary="A route that must not be emitted.",
                    keywords=("brokenroute",),
                    action_label="Open Broken",
                    action_type="platform",
                ),
            ),
            allowed_routes=frozenset(
                {
                    "/document-expiry-tracker",
                    "/salary-breakdown-calculator",
                    "/net-worth-tracker",
                    "/savings-goal-planner",
                    "/expense-tracker",
                    "/about",
                    "/pricing",
                    "/faq",
                    "/contact",
                    "/privacy",
                    "/terms",
                    "/apps",
                }
            ),
        )

    def assert_action(self, response, route):
        self.assertTrue(any(action.route == route for action in response.actions))

    def test_exact_partial_alias_and_category_app_matches(self):
        response = query_index("Document Expiry Tracker", self.index)
        self.assertEqual(response.sources[0].title, "Document Expiry Tracker")
        self.assert_action(response, "/document-expiry-tracker")
        self.assertEqual(response.response_mode, "deterministic")

        response = query_index("salary breakdown", self.index)
        self.assertEqual(response.sources[0].title, "Salary Breakdown Calculator")

        response = query_index("passport", self.index)
        self.assertEqual(response.sources[0].title, "Document Expiry Tracker")

        response = query_index("finance", self.index)
        self.assertLessEqual(len(response.actions), 3)
        self.assertTrue(all(action.type == "app" for action in response.actions))

    def test_platform_page_matches(self):
        cases = [
            ("what is ansiversa", "/about"),
            ("pricing", "/pricing"),
            ("faq", "/faq"),
            ("contact support", "/contact"),
            ("privacy", "/privacy"),
            ("terms", "/terms"),
        ]
        for message, route in cases:
            with self.subTest(message=message):
                response = query_index(message, self.index)
                self.assert_action(response, route)
                self.assertIn(response.confidence, {"high", "medium"})
                self.assertEqual(response.response_mode, "deterministic")

    def test_unknown_fallback_has_no_sources(self):
        response = query_index("zzzz unknown nothing", self.index)
        self.assertEqual(response.confidence, "low")
        self.assertEqual(response.response_mode, "fallback")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.actions[0], AssistantAction(type="platform", label="Browse Apps", route="/apps"))

    def test_financial_advice_question_returns_safety_guidance(self):
        response = query_index("Can Ansiversa give financial advice?", self.index, answer_provider=FakeProvider())
        self.assertEqual(response.confidence, "high")
        self.assertEqual(response.response_mode, "deterministic")
        self.assertIn("does not provide professional financial advice", response.answer)
        self.assert_action(response, "/salary-breakdown-calculator")
        self.assert_action(response, "/savings-goal-planner")
        self.assertFalse(any(source.title == "About" for source in response.sources))

    def test_explicit_out_of_scope_question_does_not_route_to_about(self):
        response = query_index("Tell me something that is not in Ansiversa.", self.index, answer_provider=FakeProvider())
        self.assertEqual(response.confidence, "low")
        self.assertEqual(response.response_mode, "fallback")
        self.assertIn("could not find that topic", response.answer)
        self.assertIn("apps, platform features, pricing, accounts, navigation, and policies", response.answer)
        self.assertFalse(any(action.route == "/about" for action in response.actions))

    def test_invalid_routes_are_not_emitted(self):
        response = query_index("brokenroute", self.index)
        self.assertFalse(any(action.route == "/not-allowed" for action in response.actions))

    def test_internal_entries_do_not_leak(self):
        response = query_index("agents credentials secrets", self.index)
        combined = f"{response.answer} {' '.join(source.title for source in response.sources)}"
        self.assertNotIn("Secrets", combined)
        self.assertNotIn("AGENTS", combined)

    def test_strong_app_query_uses_grounded_openai(self):
        provider = FakeProvider("Document Expiry Tracker helps you monitor renewal deadlines.")
        response = query_index("Document Expiry Tracker", self.index, answer_provider=provider)
        self.assertEqual(response.response_mode, "openai_grounded")
        self.assertEqual(response.answer, "Document Expiry Tracker helps you monitor renewal deadlines.")
        self.assertEqual(len(provider.calls), 1)
        self.assert_action(response, "/document-expiry-tracker")

    def test_platform_page_skips_openai(self):
        provider = FakeProvider()
        response = query_index("pricing", self.index, answer_provider=provider)
        self.assertEqual(response.response_mode, "deterministic")
        self.assertEqual(provider.calls, [])
        self.assert_action(response, "/pricing")

    def test_no_match_skips_openai_and_does_not_fabricate(self):
        provider = FakeProvider()
        response = query_index("unknown beta roadmap feature", self.index, answer_provider=provider)
        self.assertEqual(response.response_mode, "fallback")
        self.assertEqual(provider.calls, [])
        self.assertEqual(response.sources, [])
        self.assertNotIn("beta roadmap", response.answer.lower())

    def test_provider_timeout_exception_and_empty_output_fallback(self):
        for error in (TimeoutError("timeout"), OpenAIProviderError("failed"), RuntimeError("failed")):
            with self.subTest(error=type(error).__name__):
                response = query_index(
                    "Document Expiry Tracker",
                    self.index,
                    answer_provider=FakeProvider(error=error),
                )
                self.assertEqual(response.response_mode, "deterministic")
                self.assertIn("Document Expiry Tracker is an Ansiversa app", response.answer)

        response = query_index("Document Expiry Tracker", self.index, answer_provider=FakeProvider(""))
        self.assertEqual(response.response_mode, "deterministic")

    def test_model_output_cannot_create_routes_or_actions(self):
        response = query_index(
            "Document Expiry Tracker",
            self.index,
            answer_provider=FakeProvider("Open /admin/secrets now."),
        )
        self.assertEqual(response.response_mode, "openai_grounded")
        self.assertFalse(any(action.route == "/admin/secrets" for action in response.actions))
        self.assertTrue(
            all(
                action.route
                in {
                    "/document-expiry-tracker",
                    "/salary-breakdown-calculator",
                    "/net-worth-tracker",
                    "/savings-goal-planner",
                    "/about",
                    "/pricing",
                    "/faq",
                    "/contact",
                    "/privacy",
                    "/terms",
                    "/apps",
                }
                for action in response.actions
            )
        )

    def test_provider_receives_only_bounded_public_context(self):
        provider = FakeProvider()
        response = query_index(
            "Document Expiry Tracker",
            self.index,
            answer_provider=provider,
            max_context_chars=180,
        )
        self.assertEqual(response.response_mode, "openai_grounded")
        context = provider.calls[0]["context"]
        self.assertLessEqual(len(context), 180)
        self.assertIn("Document Expiry Tracker", context)
        self.assertNotIn("AGENTS", context)
        self.assertNotIn("Secrets", context)
        self.assertNotIn("credentials", context)
        self.assertNotIn("/document-expiry-tracker", context)

    def test_simple_app_navigation_skips_openai(self):
        provider = FakeProvider()
        response = query_index("open Document Expiry Tracker", self.index, answer_provider=provider)
        self.assertEqual(response.response_mode, "deterministic")
        self.assertEqual(provider.calls, [])
        self.assert_action(response, "/document-expiry-tracker")

    def test_multiple_app_matches_have_max_three_deterministic_actions(self):
        response = query_index("finance", self.index, answer_provider=FakeProvider())
        self.assertLessEqual(len(response.actions), 3)
        self.assertTrue(all(action.type == "app" for action in response.actions))

    def test_request_rejects_empty_and_long_messages(self):
        with self.assertRaises(ValidationError):
            AssistantQueryRequest(message="   ")

        with self.assertRaises(ValidationError):
            AssistantQueryRequest(message="x" * 2001)


if __name__ == "__main__":
    unittest.main()
