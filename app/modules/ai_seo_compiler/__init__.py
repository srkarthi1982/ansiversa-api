"""Disabled AI SEO compiler foundation.

Phase 1 exposes pure model and fixture helpers for isolated tests only. This
package is not imported by runtime routes, startup, the Knowledge builder, or
the public publisher.
"""

from app.modules.ai_seo_compiler.fixtures import ValidationFixture, validate_fixture
from app.modules.ai_seo_compiler.inventory import SourceInventory, SourceInventoryItem, classify_source
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json

COMPILER_RUNTIME_ENABLED = False

__all__ = [
    "COMPILER_RUNTIME_ENABLED",
    "SourceInventory",
    "SourceInventoryItem",
    "ValidationFixture",
    "classify_source",
    "stable_digest",
    "stable_json",
    "validate_fixture",
]
