"""Validation and conflict detection for isolated compiler candidates."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from app.modules.ai_seo_compiler.fixtures import ValidationFixture, validate_fixture
from app.modules.ai_seo_compiler.inventory import SourceVisibility
from app.modules.ai_seo_compiler.normalization import canonical_url, normalize_route
from app.modules.ai_seo_compiler.parser import ParsedClaim


class Severity(StrEnum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


BLOCKING_SEVERITIES = {Severity.BLOCKER, Severity.CRITICAL, Severity.MAJOR}


class ValidationCode(StrEnum):
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    VISIBILITY_VIOLATION = "visibility_violation"
    STALE_REQUIRED_TRUTH = "stale_required_truth"
    CONFLICTING_AUTHORITY = "conflicting_authority"
    INVALID_ROUTE = "invalid_route"
    UNSAFE_CONTENT = "unsafe_content"
    DUPLICATE_IDENTITY = "duplicate_identity"
    UNSUPPORTED_GRAPH_PROPERTY = "unsupported_graph_property"
    MANIFEST_LEAKAGE = "manifest_leakage"
    UNRESOLVED_RELATIONSHIP = "unresolved_relationship"
    APP_101_PROHIBITED = "app_101_prohibited"
    RELEASE_BLOCKED = "release_blocked"


@dataclass(frozen=True)
class ValidationFinding:
    severity: Severity
    code: ValidationCode
    message: str
    subject: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "code": self.code.value,
            "message": self.message,
            "subject": self.subject,
        }


@dataclass(frozen=True)
class ConflictRecord:
    field_name: str
    values: tuple[str, ...]
    sources: tuple[dict[str, str], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "fieldName": self.field_name,
            "values": list(self.values),
            "sources": list(self.sources),
        }


@dataclass(frozen=True)
class ValidationResult:
    findings: tuple[ValidationFinding, ...] = ()
    conflicts: tuple[ConflictRecord, ...] = ()

    @property
    def passed(self) -> bool:
        return not any(finding.severity in BLOCKING_SEVERITIES for finding in self.findings)

    @property
    def blocks_release(self) -> bool:
        return not self.passed

    def severity_summary(self) -> dict[str, int]:
        counts = Counter(finding.severity.value for finding in self.findings)
        return {severity.value: counts.get(severity.value, 0) for severity in Severity}

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "blocksRelease": self.blocks_release,
            "severitySummary": self.severity_summary(),
            "findings": [finding.as_dict() for finding in self.findings],
            "conflicts": [conflict.as_dict() for conflict in self.conflicts],
        }


def merge_results(*results: ValidationResult) -> ValidationResult:
    return ValidationResult(
        findings=tuple(finding for result in results for finding in result.findings),
        conflicts=tuple(conflict for result in results for conflict in result.conflicts),
    )


def validate_fixtures(fixtures: Iterable[ValidationFixture]) -> ValidationResult:
    findings: list[ValidationFinding] = []
    for fixture in fixtures:
        try:
            validate_fixture(fixture)
        except ValueError as exc:
            findings.append(ValidationFinding(Severity.CRITICAL, ValidationCode.UNSAFE_CONTENT, str(exc), fixture.fixture_id))
        if fixture.expected_visibility is SourceVisibility.GOVERNANCE_ONLY:
            findings.append(
                ValidationFinding(
                    Severity.BLOCKER,
                    ValidationCode.VISIBILITY_VIOLATION,
                    "Governance-only fixture cannot become public output without explicit policy",
                    fixture.fixture_id,
                )
            )
        if fixture.review_state in {"stale", "unreviewed"}:
            findings.append(
                ValidationFinding(
                    Severity.MAJOR,
                    ValidationCode.STALE_REQUIRED_TRUTH,
                    f"Required truth is {fixture.review_state}",
                    fixture.fixture_id,
                )
            )
    return ValidationResult(tuple(findings))


def detect_conflicts(claims: Iterable[ParsedClaim]) -> ValidationResult:
    by_field: dict[str, list[ParsedClaim]] = {}
    for claim in claims:
        by_field.setdefault(claim.field_name, []).append(claim)
    findings: list[ValidationFinding] = []
    conflicts: list[ConflictRecord] = []
    for field_name, items in sorted(by_field.items()):
        values = tuple(sorted({item.value for item in items}))
        if len(values) > 1:
            conflicts.append(
                ConflictRecord(
                    field_name=field_name,
                    values=values,
                    sources=tuple(item.provenance.as_dict() for item in sorted(items, key=lambda claim: claim.provenance.path)),
                )
            )
            findings.append(
                ValidationFinding(
                    Severity.CRITICAL,
                    ValidationCode.CONFLICTING_AUTHORITY,
                    "Conflicting authoritative values must fail closed",
                    field_name,
                )
            )
    return ValidationResult(tuple(findings), tuple(conflicts))


def validate_required_fields(record: dict[str, object], required: Iterable[str], *, subject: str) -> ValidationResult:
    findings = [
        ValidationFinding(Severity.BLOCKER, ValidationCode.MISSING_REQUIRED_FIELD, f"Missing required field: {field}", subject)
        for field in required
        if field not in record or record[field] in {None, "", ()}
    ]
    return ValidationResult(tuple(findings))


def validate_route_pair(route: str, url: str, *, subject: str) -> ValidationResult:
    try:
        expected = canonical_url(normalize_route(route))
    except ValueError as exc:
        return ValidationResult((ValidationFinding(Severity.BLOCKER, ValidationCode.INVALID_ROUTE, str(exc), subject),))
    if expected != url:
        return ValidationResult(
            (ValidationFinding(Severity.BLOCKER, ValidationCode.INVALID_ROUTE, "Canonical URL does not match route", subject),)
        )
    return ValidationResult()
