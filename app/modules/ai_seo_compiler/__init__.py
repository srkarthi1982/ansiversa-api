"""Disabled AI SEO compiler foundation.

Phase 6 adds operational evidence helpers in an isolated submodule. The compiler
remains disabled by default and is not imported by runtime routes or application
startup.
"""

from app.modules.ai_seo_compiler.fixtures import ValidationFixture, validate_fixture
from app.modules.ai_seo_compiler.integration import (
    AI_SEO_CONTROLLED_INTEGRATION_DEFAULT,
    ControlledIntegrationControl,
    run_controlled_integration,
)
from app.modules.ai_seo_compiler.pipeline import CompilerInput, CompilerOutput, compile_candidate
from app.modules.ai_seo_compiler.readiness import validate_production_readiness
from app.modules.ai_seo_compiler.inventory import SourceInventory, SourceInventoryItem, classify_source
from app.modules.ai_seo_compiler.serialization import stable_digest, stable_json
from app.modules.ai_seo_compiler.shadow import compare_shadow_snapshots

COMPILER_RUNTIME_ENABLED = False

__all__ = [
    "COMPILER_RUNTIME_ENABLED",
    "AI_SEO_CONTROLLED_INTEGRATION_DEFAULT",
    "SourceInventory",
    "SourceInventoryItem",
    "ValidationFixture",
    "CompilerInput",
    "CompilerOutput",
    "ControlledIntegrationControl",
    "classify_source",
    "compile_candidate",
    "compare_shadow_snapshots",
    "run_controlled_integration",
    "stable_digest",
    "stable_json",
    "validate_production_readiness",
    "validate_fixture",
]
