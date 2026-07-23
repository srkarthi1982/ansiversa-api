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


CANONICAL_MANIFEST_KEY = "public-seo-projection"


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


def _ordered_items(items: list[ShadowComparableItem]) -> tuple[ShadowComparableItem, ...]:
    return tuple(sorted(items, key=lambda item: item.identity))


def _route_from_url(url: str) -> str:
    prefix = "https://ansiversa.com"
    if url == prefix:
        return "/"
    if url.startswith(prefix):
        return url[len(prefix):]
    return url


def _canonical_entity_payload(*, route: object, canonical_url: object, name: object, summary: object, capabilities: object) -> dict[str, Any]:
    capability_values = list(capabilities) if isinstance(capabilities, list | tuple) else []
    return {
        "route": str(route),
        "canonicalUrl": str(canonical_url),
        "visibleContent": {
            "name": str(name),
            "summary": str(summary),
            "capabilities": sorted(dict.fromkeys(str(value) for value in capability_values)),
        },
    }


def _canonical_metadata_payload(*, route: object, canonical: object, description: object) -> dict[str, Any]:
    return {
        "route": str(route),
        "canonical": str(canonical),
        "description": str(description),
    }


def _canonical_graph_payload(node: dict[str, Any]) -> dict[str, Any] | None:
    if node.get("@type") != "SoftwareApplication":
        return None
    canonical_url = str(node.get("url") or "")
    return {
        "@type": "SoftwareApplication",
        "route": _route_from_url(canonical_url),
        "canonicalUrl": canonical_url,
        "name": str(node.get("name") or ""),
        "description": str(node.get("description") or ""),
        "applicationCategory": str(node.get("applicationCategory") or ""),
    }


def _semantic_items_for_manifest(items: list[ShadowComparableItem]) -> list[ShadowComparableItem]:
    return [item for item in items if item.kind is not ShadowItemKind.MANIFEST]


def _manifest_payload(items: list[ShadowComparableItem]) -> dict[str, object]:
    semantic_items = _semantic_items_for_manifest(items)
    entity_payloads = [item.payload for item in _ordered_items(semantic_items) if item.kind is ShadowItemKind.ENTITY]
    graph_payloads = [item.payload for item in _ordered_items(semantic_items) if item.kind is ShadowItemKind.GRAPH]
    metadata_payloads = [item.payload for item in _ordered_items(semantic_items) if item.kind is ShadowItemKind.METADATA]
    routes = sorted({str(item.payload.get("route")) for item in semantic_items if item.payload.get("route")})
    canonical_urls = sorted(
        {
            str(item.payload.get("canonicalUrl", item.payload.get("canonical")))
            for item in semantic_items
            if item.payload.get("canonicalUrl", item.payload.get("canonical"))
        }
    )
    return {
        "appCount": len(entity_payloads),
        "routeSetDigest": stable_digest(routes),
        "canonicalUrlSetDigest": stable_digest(canonical_urls),
        "entityProjectionDigest": stable_digest(entity_payloads),
        "graphProjectionDigest": stable_digest(graph_payloads),
        "metadataProjectionDigest": stable_digest(metadata_payloads),
    }


def _append_canonical_manifest(items: list[ShadowComparableItem]) -> None:
    items.append(
        ShadowComparableItem.from_payload(
            kind=ShadowItemKind.MANIFEST,
            key=CANONICAL_MANIFEST_KEY,
            payload=_manifest_payload(items),
        )
    )


def snapshot_from_compiler_output(output: CompilerOutput, *, source_name: str = "AI SEO Compiler Candidate") -> ShadowSnapshot:
    items: list[ShadowComparableItem] = []
    validation_report = output.validation_report.as_dict()
    if output.public_render_manifest is not None:
        manifest = output.public_render_manifest.as_dict()
        for bundle in manifest["pageBundles"]:
            bundle_payload = dict(bundle)
            visible_content = bundle_payload["visibleContent"]
            items.append(
                ShadowComparableItem.from_payload(
                    kind=ShadowItemKind.ENTITY,
                    key=str(bundle_payload["route"]),
                    payload=_canonical_entity_payload(
                        route=bundle_payload["route"],
                        canonical_url=bundle_payload["canonicalUrl"],
                        name=visible_content["name"],
                        summary=visible_content["summary"],
                        capabilities=visible_content["capabilities"],
                    ),
                )
            )
            items.append(
                ShadowComparableItem.from_payload(
                    kind=ShadowItemKind.METADATA,
                    key=str(bundle_payload["route"]),
                    payload=_canonical_metadata_payload(
                        route=bundle_payload["route"],
                        canonical=bundle_payload["metadata"]["canonical"],
                        description=bundle_payload["metadata"]["description"],
                    ),
                )
            )
    if output.graph is not None:
        for node in output.graph.nodes:
            graph_payload = _canonical_graph_payload(dict(node))
            if graph_payload is not None:
                items.append(ShadowComparableItem.from_payload(kind=ShadowItemKind.GRAPH, key=str(graph_payload["route"]), payload=graph_payload))
    _append_canonical_manifest(items)

    return ShadowSnapshot(
        source_name=source_name,
        release_id=str(validation_report["releaseId"]),
        items=_ordered_items(items),
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
                payload=_canonical_entity_payload(
                    route=app["route"],
                    canonical_url=app["canonicalUrl"],
                    name=app["name"],
                    summary=app["description"],
                    capabilities=app["capabilities"],
                ),
            )
        )
        metadata = metadata_by_route.get(app["route"], {})
        items.append(
            ShadowComparableItem.from_payload(
                kind=ShadowItemKind.METADATA,
                key=str(app["route"]),
                payload=_canonical_metadata_payload(
                    route=app["route"],
                    canonical=metadata.get("canonical", app["canonicalUrl"]),
                    description=metadata.get("description", app["description"]),
                ),
            )
        )
    for node in artifacts.jsonld["@graph"]:
        graph_payload = _canonical_graph_payload(dict(node))
        if graph_payload is not None:
            items.append(ShadowComparableItem.from_payload(kind=ShadowItemKind.GRAPH, key=str(graph_payload["route"]), payload=graph_payload))
    _append_canonical_manifest(items)
    return ShadowSnapshot(
        source_name="Current Knowledge Publisher",
        release_id=release_id,
        items=_ordered_items(items),
        validation_summary={severity.value: 0 for severity in Severity},
        validation_passed=True,
    )


def stable_report_json(report: ShadowComparisonReport) -> str:
    return stable_json(report.as_dict())
