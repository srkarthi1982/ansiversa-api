"""Internal validation report models for Phase 2 compiler candidates."""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.ai_seo_compiler.validation import ValidationResult


@dataclass(frozen=True)
class ValidationReport:
    release_id: str
    validation: ValidationResult
    source_count: int
    entity_count: int
    graph_passed: bool
    manifest_passed: bool
    omitted_fields: tuple[dict[str, str], ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "releaseId": self.release_id,
            "passed": self.validation.passed and self.graph_passed and self.manifest_passed,
            "severitySummary": self.validation.severity_summary(),
            "findings": [finding.as_dict() for finding in self.validation.findings],
            "conflicts": [conflict.as_dict() for conflict in self.validation.conflicts],
            "omittedFields": list(self.omitted_fields),
            "sourceCount": self.source_count,
            "entityCount": self.entity_count,
            "graphValidation": {"passed": self.graph_passed},
            "manifestValidation": {"passed": self.manifest_passed},
        }
