"""Bounded validation fixture helpers for the disabled AI SEO compiler."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.modules.ai_seo_compiler.inventory import SourceInventoryItem, SourceVisibility

MAX_FIXTURE_ID = 80
MAX_CLAIM_TEXT = 500
MAX_CLAIMS = 20

FORBIDDEN_FIXTURE_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    "authorization": re.compile(r"authorization\s*:\s*bearer\s+\S+", re.I),
    "database-url": re.compile(r"(?:postgres(?:ql)?|mysql|libsql)://[^\s\"]+", re.I),
    "environment-secret": re.compile(r"(?:API_KEY|TOKEN|PASSWORD|DATABASE_URL)\s*=\s*[^\s\"]+", re.I),
}


@dataclass(frozen=True)
class ValidationFixture:
    fixture_id: str
    source: SourceInventoryItem
    claims: tuple[str, ...]
    expected_visibility: SourceVisibility = SourceVisibility.PUBLIC
    review_state: str = "current"

    def __post_init__(self) -> None:
        if not self.fixture_id or len(self.fixture_id) > MAX_FIXTURE_ID:
            raise ValueError("Validation fixture id is required and bounded")
        if len(self.claims) > MAX_CLAIMS:
            raise ValueError("Validation fixture claim count exceeds bound")
        object.__setattr__(self, "expected_visibility", SourceVisibility(self.expected_visibility))
        if self.review_state not in {"current", "stale", "unreviewed"}:
            raise ValueError("Validation fixture review_state is unsupported")

    def as_dict(self) -> dict[str, object]:
        return {
            "fixtureId": self.fixture_id,
            "source": self.source.as_dict(),
            "claims": list(self.claims),
            "expectedVisibility": self.expected_visibility.value,
            "reviewState": self.review_state,
        }


def validate_fixture(fixture: ValidationFixture) -> None:
    if fixture.expected_visibility is SourceVisibility.PROHIBITED:
        raise ValueError("Validation fixture cannot expect prohibited public output")
    if fixture.source.visibility is SourceVisibility.PROHIBITED:
        raise ValueError("Prohibited source visibility cannot enter validation fixture")
    for claim in fixture.claims:
        if not claim.strip():
            raise ValueError("Validation fixture claims must not be empty")
        if len(claim) > MAX_CLAIM_TEXT:
            raise ValueError("Validation fixture claim exceeds bound")
        for label, pattern in FORBIDDEN_FIXTURE_PATTERNS.items():
            if pattern.search(claim):
                raise ValueError(f"Unsafe fixture data detected: {label}")
