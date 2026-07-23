"""Internal shadow comparison helpers for AI SEO compiler candidates.

The comparator operates on supplied in-memory snapshots only. It does not build,
write, publish, serve, or replace Knowledge artifacts.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from app.modules.ai_seo_compiler.pipeline import CompilerOutput
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.ai_seo_compiler.validation import BLOCKING_SEVERITIES, Severity


class ShadowItemKind(StrEnum):
    ENTITY = "entity"
    GRAPH = "graph"
    MANIFEST = "manifest"
    METADATA = "metadata"


class ShadowFindingCode(StrEnum):
    ENTITY_DIFFERENCE = "entity_difference"
    GRAPH_DIFFERENCE = "graph_difference"
    MANIFEST_DIFFERENCE = "manifest_difference"
    METADATA_DIFFERENCE = "metadata_difference"
    CANONICAL_URL_DIFFERENCE = "canonical_url_difference"
    DIGEST_MISMATCH = "digest_mismatch"
    MISSING_ITEM = "missing_item"
    UNEXPECTED_ITEM = "unexpected_item"
    DUPLICATE_ITEM = "duplicate_item"
    ORDERING_DIFFERENCE = "ordering_difference"
    VALIDATION_SEVERITY_DIFFERENCE = "validation_severity_difference"
    RELEASE_BLOCKED = "release_blocked"


@dataclass(frozen=True)
class ShadowComparableItem:
    kind: ShadowItemKind
    key: str
    payload: dict[str, Any]
    digest: str

    @classmethod
    def from_payload(
        cls,
        *,
        kind: ShadowItemKind,
        key: str,
        payload: dict[str, Any],
        digest: str | None = None,
    ) -> "ShadowComparableItem":
        return cls(kind=kind, key=key, payload=payload, digest=digest or stable_digest(payload))

    @property
    def identity(self) -> str:
        return f"{self.kind.value}:{self.key}"

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "key": self.key,
            "digest": self.digest,
            "payload": self.payload,
        }


@dataclass(frozen=True)
class ShadowSnapshot:
    source_name: str
    release_id: str
    items: tuple[ShadowComparableItem, ...]
    validation_summary: dict[str, int]
    validation_passed: bool = True

    def ordered_identities(self) -> tuple[str, ...]:
        return tuple(item.identity for item in self.items)

    def as_dict(self) -> dict[str, object]:
        return {
            "sourceName": self.source_name,
            "releaseId": self.release_id,
            "items": [item.as_dict() for item in self.items],
            "validationSummary": {severity.value: self.validation_summary.get(severity.value, 0) for severity in Severity},
            "validationPassed": self.validation_passed,
        }


@dataclass(frozen=True)
class ShadowFinding:
    severity: Severity
    code: ShadowFindingCode
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
class ShadowComparisonReport:
    release_id: str
    current_source: str
    candidate_source: str
    current_release_id: str
    candidate_release_id: str
    matching_items: tuple[str, ...]
    matching_entities: tuple[str, ...]
    mismatches: tuple[ShadowFinding, ...]
    missing_items: tuple[ShadowFinding, ...]
    unexpected_items: tuple[ShadowFinding, ...]
    findings: tuple[ShadowFinding, ...]

    @property
    def passed(self) -> bool:
        return not any(finding.severity in BLOCKING_SEVERITIES for finding in self.findings)

    def severity_summary(self) -> dict[str, int]:
        counts = Counter(finding.severity.value for finding in self.findings)
        return {severity.value: counts.get(severity.value, 0) for severity in Severity}

    def as_dict(self) -> dict[str, object]:
        return {
            "releaseId": self.release_id,
            "currentSource": self.current_source,
            "candidateSource": self.candidate_source,
            "currentReleaseId": self.current_release_id,
            "candidateReleaseId": self.candidate_release_id,
            "passed": self.passed,
            "recommendation": "pass" if self.passed else "fail_closed",
            "summary": {
                "matchingItems": len(self.matching_items),
                "matchingEntities": len(self.matching_entities),
                "mismatches": len(self.mismatches),
                "missingItems": len(self.missing_items),
                "unexpectedItems": len(self.unexpected_items),
                "findings": len(self.findings),
            },
            "matchingItems": list(self.matching_items),
            "matchingEntities": list(self.matching_entities),
            "mismatches": [finding.as_dict() for finding in self.mismatches],
            "missingItems": [finding.as_dict() for finding in self.missing_items],
            "unexpectedItems": [finding.as_dict() for finding in self.unexpected_items],
            "severitySummary": self.severity_summary(),
            "findings": [finding.as_dict() for finding in self.findings],
        }


def _items_by_identity(snapshot: ShadowSnapshot) -> dict[str, tuple[ShadowComparableItem, ...]]:
    grouped: dict[str, list[ShadowComparableItem]] = {}
    for item in snapshot.items:
        grouped.setdefault(item.identity, []).append(item)
    return {identity: tuple(items) for identity, items in grouped.items()}


def _difference_code(item: ShadowComparableItem) -> ShadowFindingCode:
    if item.kind is ShadowItemKind.ENTITY:
        return ShadowFindingCode.ENTITY_DIFFERENCE
    if item.kind is ShadowItemKind.GRAPH:
        return ShadowFindingCode.GRAPH_DIFFERENCE
    if item.kind is ShadowItemKind.MANIFEST:
        return ShadowFindingCode.MANIFEST_DIFFERENCE
    return ShadowFindingCode.METADATA_DIFFERENCE


def _canonical_value(payload: dict[str, Any]) -> object:
    return payload.get("canonicalUrl", payload.get("canonical"))


def compare_shadow_snapshots(current: ShadowSnapshot, candidate: ShadowSnapshot) -> ShadowComparisonReport:
    current_items = _items_by_identity(current)
    candidate_items = _items_by_identity(candidate)
    findings: list[ShadowFinding] = []
    mismatches: list[ShadowFinding] = []
    missing_items: list[ShadowFinding] = []
    unexpected_items: list[ShadowFinding] = []
    matching: list[str] = []

    for snapshot_name, grouped in ((current.source_name, current_items), (candidate.source_name, candidate_items)):
        for identity, items in sorted(grouped.items()):
            if len(items) > 1:
                findings.append(
                    ShadowFinding(
                        Severity.BLOCKER,
                        ShadowFindingCode.DUPLICATE_ITEM,
                        f"Duplicate comparable item in {snapshot_name}",
                        identity,
                    )
                )

    for identity in sorted(set(current_items) - set(candidate_items)):
        finding = ShadowFinding(Severity.BLOCKER, ShadowFindingCode.MISSING_ITEM, "Candidate output is missing current item", identity)
        findings.append(finding)
        missing_items.append(finding)

    for identity in sorted(set(candidate_items) - set(current_items)):
        finding = ShadowFinding(Severity.BLOCKER, ShadowFindingCode.UNEXPECTED_ITEM, "Candidate output contains unexpected item", identity)
        findings.append(finding)
        unexpected_items.append(finding)

    for identity in sorted(set(current_items) & set(candidate_items)):
        current_group = current_items[identity]
        candidate_group = candidate_items[identity]
        if len(current_group) != 1 or len(candidate_group) != 1:
            continue
        current_item = current_group[0]
        candidate_item = candidate_group[0]
        if _canonical_value(current_item.payload) != _canonical_value(candidate_item.payload):
            finding = ShadowFinding(
                Severity.CRITICAL,
                ShadowFindingCode.CANONICAL_URL_DIFFERENCE,
                "Canonical URL differs between current and candidate output",
                identity,
            )
            findings.append(finding)
            mismatches.append(finding)
        elif current_item.payload != candidate_item.payload:
            finding = ShadowFinding(
                Severity.CRITICAL,
                _difference_code(current_item),
                "Comparable payload differs between current and candidate output",
                identity,
            )
            findings.append(finding)
            mismatches.append(finding)
        elif current_item.digest != candidate_item.digest:
            finding = ShadowFinding(
                Severity.CRITICAL,
                ShadowFindingCode.DIGEST_MISMATCH,
                "Comparable digest differs while payload is equivalent",
                identity,
            )
            findings.append(finding)
            mismatches.append(finding)
        else:
            matching.append(identity)

    if set(current.ordered_identities()) == set(candidate.ordered_identities()) and current.ordered_identities() != candidate.ordered_identities():
        findings.append(
            ShadowFinding(
                Severity.MAJOR,
                ShadowFindingCode.ORDERING_DIFFERENCE,
                "Comparable item ordering differs between current and candidate output",
                "item-order",
            )
        )

    if _severity_summary(current) != _severity_summary(candidate):
        findings.append(
            ShadowFinding(
                Severity.MAJOR,
                ShadowFindingCode.VALIDATION_SEVERITY_DIFFERENCE,
                "Validation severity summary differs between current and candidate output",
                "validation-summary",
            )
        )

    for snapshot in (current, candidate):
        if not snapshot.validation_passed:
            findings.append(
                ShadowFinding(
                    Severity.BLOCKER,
                    ShadowFindingCode.RELEASE_BLOCKED,
                    f"{snapshot.source_name} validation did not pass",
                    snapshot.release_id,
                )
            )

    ordered_findings = tuple(sorted(findings, key=lambda finding: (finding.subject, finding.code.value, finding.severity.value)))
    return ShadowComparisonReport(
        release_id=f"shadow-{stable_digest({'current': current.as_dict(), 'candidate': candidate.as_dict()})[:16]}",
        current_source=current.source_name,
        candidate_source=candidate.source_name,
        current_release_id=current.release_id,
        candidate_release_id=candidate.release_id,
        matching_items=tuple(sorted(matching)),
        matching_entities=tuple(sorted(identity for identity in matching if identity.startswith(f"{ShadowItemKind.ENTITY.value}:"))),
        mismatches=tuple(sorted(mismatches, key=lambda finding: (finding.subject, finding.code.value))),
        missing_items=tuple(sorted(missing_items, key=lambda finding: finding.subject)),
        unexpected_items=tuple(sorted(unexpected_items, key=lambda finding: finding.subject)),
        findings=ordered_findings,
    )


def _severity_summary(snapshot: ShadowSnapshot) -> dict[str, int]:
    return {severity.value: snapshot.validation_summary.get(severity.value, 0) for severity in Severity}


def snapshot_from_compiler_output(output: CompilerOutput, *, source_name: str = "AI SEO Compiler Candidate") -> ShadowSnapshot:
    items: list[ShadowComparableItem] = []
    validation_report = output.validation_report.as_dict()
    if output.public_render_manifest is not None:
        manifest = output.public_render_manifest.as_dict()
        items.append(ShadowComparableItem.from_payload(kind=ShadowItemKind.MANIFEST, key="public-render-manifest", payload=manifest))
        for bundle in manifest["pageBundles"]:
            bundle_payload = dict(bundle)
            items.append(
                ShadowComparableItem.from_payload(
                    kind=ShadowItemKind.ENTITY,
                    key=str(bundle_payload["route"]),
                    payload={
                        "route": bundle_payload["route"],
                        "canonicalUrl": bundle_payload["canonicalUrl"],
                        "visibleContent": bundle_payload["visibleContent"],
                    },
                )
            )
            items.append(
                ShadowComparableItem.from_payload(
                    kind=ShadowItemKind.METADATA,
                    key=str(bundle_payload["route"]),
                    payload={
                        "route": bundle_payload["route"],
                        "canonical": bundle_payload["metadata"]["canonical"],
                        "title": bundle_payload["metadata"]["title"],
                        "description": bundle_payload["metadata"]["description"],
                    },
                )
            )
    if output.graph is not None:
        for node in output.graph.nodes:
            items.append(ShadowComparableItem.from_payload(kind=ShadowItemKind.GRAPH, key=str(node["@id"]), payload=dict(node)))

    return ShadowSnapshot(
        source_name=source_name,
        release_id=str(validation_report["releaseId"]),
        items=tuple(items),
        validation_summary=dict(validation_report["severitySummary"]),
        validation_passed=bool(validation_report["passed"]),
    )


def snapshot_from_knowledge_artifacts(artifacts: Any, *, release_id: str = "knowledge-current") -> ShadowSnapshot:
    knowledge = artifacts.knowledge
    metadata_by_route = {page["route"]: page for page in artifacts.metadata["pages"]}
    items: list[ShadowComparableItem] = []
    for app in knowledge["apps"]:
        items.append(
            ShadowComparableItem.from_payload(
                kind=ShadowItemKind.ENTITY,
                key=str(app["route"]),
                payload={
                    "route": app["route"],
                    "canonicalUrl": app["canonicalUrl"],
                    "visibleContent": {
                        "name": app["name"],
                        "summary": app["description"],
                        "capabilities": list(app["capabilities"]),
                    },
                },
            )
        )
        metadata = metadata_by_route.get(app["route"], {})
        items.append(
            ShadowComparableItem.from_payload(
                kind=ShadowItemKind.METADATA,
                key=str(app["route"]),
                payload={
                    "route": app["route"],
                    "canonical": metadata.get("canonical", app["canonicalUrl"]),
                    "title": metadata.get("title", app["name"]),
                    "description": metadata.get("description", app["description"]),
                },
            )
        )
    for node in artifacts.jsonld["@graph"]:
        items.append(ShadowComparableItem.from_payload(kind=ShadowItemKind.GRAPH, key=str(node["@id"]), payload=dict(node)))
    items.append(
        ShadowComparableItem.from_payload(
            kind=ShadowItemKind.MANIFEST,
            key="public-artifact-set",
            payload={
                "knowledgeDigest": stable_digest(artifacts.knowledge),
                "jsonldDigest": stable_digest(artifacts.jsonld),
                "metadataDigest": stable_digest(artifacts.metadata),
                "sitemapDigest": stable_digest(artifacts.sitemap),
            },
        )
    )
    return ShadowSnapshot(
        source_name="Current Knowledge Publisher",
        release_id=release_id,
        items=tuple(sorted(items, key=lambda item: item.identity)),
        validation_summary={severity.value: 0 for severity in Severity},
        validation_passed=True,
    )


def stable_report_json(report: ShadowComparisonReport) -> str:
    return stable_json(report.as_dict())
