from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
DESIGN = ROOT / "docs" / "design"


def read(name: str) -> str:
    return (DESIGN / name).read_text(encoding="utf-8")


def test_design_freeze_has_required_artifacts() -> None:
    required = {
        "INTERVENTION_SELECTION.md",
        "MODEL_SELECTION.md",
        "DOSE_DESIGN.md",
        "OUTCOME_HIERARCHY.md",
        "SAFETY_BENCHMARK_DECISION.md",
        "UTILITY_CALIBRATION_CONSISTENCY.md",
        "GENERIC_PERTURBATION_CONTROL.md",
        "HYPOTHESES.md",
        "STATISTICAL_ANALYSIS_PLAN.md",
        "COMPUTE_FEASIBILITY.md",
        "EXPERIMENT_SIZES.md",
        "BENCHMARK_LICENSE_ACCESS.md",
        "DESIGN_DECISION_MATRIX.md",
        "CLAIM_BOUNDARY.md",
        "PILOT_DECISION_RULES.md",
        "REVIEWER_CHALLENGE.md",
    }
    assert required.issubset({path.name for path in DESIGN.glob("*.md")})


def test_model_records_have_identifiers_and_revisions() -> None:
    text = read("MODEL_SELECTION.md")
    assert text.count("| Primary | `") == 3
    assert "aa8e72537993ba99e69dfaafa59ed015b17504d1" in text
    assert "0cb88a4f764b7a12671c53f0838cd831a0843b95" in text
    assert "299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8" in text
    assert "<MODEL_ID>" not in text
    assert "TBD" not in text


def test_charter_has_at_most_three_draft_rqs_and_no_restoration_headline() -> None:
    charter = (ROOT / "docs" / "RESEARCH_CHARTER.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^- \*\*RQ\d", charter, flags=re.MULTILINE)) <= 3
    assert "Restoration is not a headline research question" in charter


def test_design_preserves_no_experiment_boundary() -> None:
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in DESIGN.glob("*.md"))
    assert "No weights were downloaded" in corpus
    assert "No benchmark files were downloaded" in corpus
    assert "DRAFT — TO BE FROZEN BEFORE CONFIRMATORY RUNS" in corpus
