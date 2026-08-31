"""Zero-inference exploratory-pilot planner and scoring primitives."""
from __future__ import annotations

import argparse
import math
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALPHAS = (-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
RANDOM_CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MODEL_REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"

@dataclass(frozen=True)
class Condition:
    checkpoint: str
    revision: str
    intervention_type: str
    control_seed: int | None
    alpha: float
    outcome: str
    item_id: str
    generation_seed: int
    baseline_reference: str | None = None


def stable_probabilities(log_scores: list[float]) -> list[float]:
    if not log_scores or not all(math.isfinite(x) for x in log_scores):
        raise ValueError("log scores must be finite and non-empty")
    pivot = max(log_scores)
    weights = [math.exp(x - pivot) for x in log_scores]
    total = sum(weights)
    if not math.isfinite(total) or total <= 0:
        raise ValueError("log-sum-exp normalization failed")
    return [w / total for w in weights]


def brier_score(probabilities: list[float], correct_index: int) -> float:
    if not 0 <= correct_index < len(probabilities):
        raise ValueError("correct index out of range")
    if not math.isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("probabilities must sum to one")
    return sum((p - (i == correct_index)) ** 2 for i, p in enumerate(probabilities))


def nll(probabilities: list[float], correct_index: int) -> float:
    if not 0 <= correct_index < len(probabilities) or probabilities[correct_index] <= 0:
        raise ValueError("correct probability must be positive")
    return -math.log(probabilities[correct_index])


def permute_options(options: list[str], permutation: list[int]) -> list[str]:
    if sorted(permutation) != list(range(len(options))):
        raise ValueError("permutation must be bijective")
    return [options[i] for i in permutation]


def remap_answer(original_index: int, permutation: list[int]) -> int:
    if original_index not in permutation:
        raise ValueError("answer index missing from permutation")
    return permutation.index(original_index)


def expand_conditions(outcome_items: dict[str, list[str]], generation_seed: int = 20260830) -> list[Condition]:
    conditions: list[Condition] = []
    for outcome, item_ids in sorted(outcome_items.items()):
        for item_id in item_ids:
            baseline_key = f"baseline:{outcome}:{item_id}:{generation_seed}"
            conditions.append(
                Condition(
                    MODEL_ID, MODEL_REVISION, "baseline", None, 0.0, outcome, item_id, generation_seed, baseline_key
                )
            )
            for alpha in ALPHAS:
                if alpha == 0.0:
                    continue
                conditions.append(
                    Condition(
                        MODEL_ID,
                        MODEL_REVISION,
                        "refusal_direction",
                        None,
                        alpha,
                        outcome,
                        item_id,
                        generation_seed,
                        baseline_key,
                    )
                )
                for seed in RANDOM_CONTROL_SEEDS:
                    conditions.append(
                        Condition(
                            MODEL_ID,
                            MODEL_REVISION,
                            "random_control",
                            seed,
                            alpha,
                            outcome,
                            item_id,
                            generation_seed,
                            baseline_key,
                        )
                    )
    return conditions


def _read_manifest(root: Path, name: str) -> dict[str, Any]:
    path = root / "configs" / "manifests" / name
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _xstest_items(data: dict[str, Any]) -> list[str]:
    safe = data.get("safe", {})
    unsafe = data.get("unsafe", {})
    ids = list(safe.get("ids", [])) + list(unsafe.get("ids", []))
    if len(ids) != len(set(ids)) or len(ids) != 24 or safe.get("count") != 12 or unsafe.get("count") != 12:
        raise ValueError("XSTest exploratory subset is not the frozen 12+12 manifest")
    return ids


def dry_run(root: Path) -> int:
    xstest = tomllib.loads((root / "configs/manifests/xstest_exploratory_pilot.toml").read_text(encoding="utf-8"))
    mmlu = _read_manifest(root, "mmlu.toml")
    consistency = _read_manifest(root, "consistency_pairs.toml")
    xstest_ids = _xstest_items(xstest)
    mmlu_ready = str(mmlu.get("status", "")).startswith("ready")
    consistency_ready = str(consistency.get("status", "")).startswith("ready") and bool(consistency.get("pairs"))
    items = {
        "xstest_safety": xstest_ids,
        "mmlu_calibration": list(mmlu.get("pilot_ids", [])) if mmlu_ready else [],
        "consistency": list(consistency.get("pair_ids", [])) if consistency_ready else [],
    }
    conditions = expand_conditions(items)
    baselines = {c.baseline_reference for c in conditions if c.intervention_type == "baseline"}
    refusal = [c for c in conditions if c.intervention_type == "refusal_direction"]
    random = [c for c in conditions if c.intervention_type == "random_control"]
    blockers = []
    if not mmlu_ready:
        blockers.append("MMLU source/subset unavailable")
    if not consistency_ready:
        blockers.append("consistency pairs unavailable because MMLU source/subset is unavailable")
    print("model_count: 1")
    print(f"model: {MODEL_ID}@{MODEL_REVISION}")
    print(f"xstest_items: {len(xstest_ids)}")
    print(f"mmlu_items: {len(items['mmlu_calibration'])}")
    print(f"consistency_pairs: {len(items['consistency'])}")
    print(f"unique_baseline_count: {len(baselines)}")
    print(f"refusal_direction_conditions: {len(refusal)}")
    print(f"random_control_conditions: {len(random)}")
    print(f"alpha_conditions: {len(ALPHAS)}")
    print(f"total_planned_conditions: {len(conditions)}")
    print(f"total_planned_generation_count: {len([c for c in conditions if c.outcome == 'xstest_safety'])}")
    print("model_inference: 0")
    print("model_weights_loaded: 0")
    print("expected_artifact_root: artifacts/runs/exploratory_pilot_dry_run/")
    if blockers:
        print("decision: EXPLORATORY_PILOT_BLOCKED")
        print("blockers: " + "; ".join(blockers))
        return 2
    print("decision: EXPLORATORY_PILOT_GO")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    return dry_run(args.root.resolve())

if __name__ == "__main__":
    raise SystemExit(main())
