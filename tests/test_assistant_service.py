import unittest

from app.modules.assistant.schemas import AssistantAction
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

    def test_unknown_fallback_has_no_sources(self):
        response = query_index("zzzz unknown nothing", self.index)
        self.assertEqual(response.confidence, "low")
        self.assertEqual(response.sources, [])
        self.assertEqual(response.actions[0], AssistantAction(type="platform", label="Browse Apps", route="/apps"))

    def test_invalid_routes_are_not_emitted(self):
        response = query_index("brokenroute", self.index)
        self.assertFalse(any(action.route == "/not-allowed" for action in response.actions))

    def test_internal_entries_do_not_leak(self):
        response = query_index("agents credentials secrets", self.index)
        combined = f"{response.answer} {' '.join(source.title for source in response.sources)}"
        self.assertNotIn("Secrets", combined)
        self.assertNotIn("AGENTS", combined)


if __name__ == "__main__":
    unittest.main()
