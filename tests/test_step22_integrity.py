from pathlib import Path

ROOT = Path(__file__).parents[1]


REQUIRED = [
    "docs/protocols/STEP_2_2_PLAN.md",
    "docs/protocols/MODEL_ACCESS_GATE.md",
    "docs/protocols/DATA_PARTITION_POLICY.md",
    "docs/protocols/DIRECTION_ESTIMATION.md",
    "docs/protocols/SITE_SELECTION.md",
    "docs/protocols/RANDOM_CONTROL_AND_MATCHING.md",
    "docs/protocols/benchmarks/XSTEST.md",
    "docs/protocols/benchmarks/HARMBENCH.md",
    "docs/protocols/HARMFUL_OUTPUT_SCORING.md",
    "docs/protocols/UTILITY_CALIBRATION_TASK.md",
    "docs/protocols/CALIBRATION_SCORING.md",
    "docs/protocols/SEMANTIC_CONSISTENCY.md",
    "configs/pilot/example.manifest.toml",
    "docs/protocols/PILOT_PROTOCOL.md",
    "docs/protocols/PILOT_OUTPUT_SCHEMA.md",
    "docs/protocols/MANUAL_VALIDATION.md",
    "docs/protocols/CONFIRMATORY_FREEZE.md",
    "docs/protocols/STATISTICAL_FREEZE.md",
    "docs/protocols/POWER_PRECISION_POLICY.md",
    "docs/protocols/ACCESS_LICENSE_FREEZE.md",
    "docs/protocols/FALLBACK_ACTIVATION.md",
]


def test_step22_protocol_files_exist() -> None:
    assert all((ROOT / path).is_file() for path in REQUIRED)


def test_protocol_keeps_target_execution_prohibited() -> None:
    text = (ROOT / "docs/protocols/STEP_2_2_PLAN.md").read_text(encoding="utf-8")
    for phrase in ("model weights", "benchmark data", "target-model loading", "scientific observations"):
        assert phrase in text


def test_access_table_does_not_claim_unqualified_clearance() -> None:
    text = (ROOT / "docs/protocols/ACCESS_LICENSE_FREEZE.md").read_text(encoding="utf-8")
    assert "blocked" in text
    assert "cleared_with_restrictions" in text
    assert "`cleared`" not in text


def test_partition_policy_forbids_silent_overlap() -> None:
    text = (ROOT / "docs/protocols/DATA_PARTITION_POLICY.md").read_text(encoding="utf-8")
    assert "must not overlap" in text
    assert "silent reuse is prohibited" in text


def test_manifest_is_placeholder_only() -> None:
    text = (ROOT / "configs/pilot/example.manifest.toml").read_text(encoding="utf-8")
    assert "PLACEHOLDER_SOURCE" in text
    assert "PLACEHOLDER_ID" in text
    assert "No dataset content" in text


def test_no_scientific_results_were_created() -> None:
    results = ROOT / "results"
    files = [p for p in results.rglob("*") if p.is_file()]
    assert [p.relative_to(results).as_posix() for p in files] == ["README.md"]
