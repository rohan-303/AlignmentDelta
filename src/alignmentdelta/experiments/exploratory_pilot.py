"""Zero-inference exploratory-pilot planning, validation, and operation accounting."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALPHAS = (-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
RANDOM_CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MODEL_REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
CACHE_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"


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
    baseline_reference: str


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
    if not all(math.isfinite(p) and p >= 0 for p in probabilities):
        raise ValueError("probabilities must be finite and non-negative")
    if not math.isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("probabilities must sum to one")
    return sum((p - (i == correct_index)) ** 2 for i, p in enumerate(probabilities))


def nll(probabilities: list[float], correct_index: int) -> float:
    if (
        not 0 <= correct_index < len(probabilities)
        or not math.isfinite(probabilities[correct_index])
        or probabilities[correct_index] <= 0
    ):
        raise ValueError("correct probability must be positive and finite")
    return -math.log(probabilities[correct_index])


def ece(probabilities: list[float], correct: list[bool], bins: int = 10) -> float:
    if (
        len(probabilities) != len(correct)
        or bins <= 0
        or not all(0 <= p <= 1 and math.isfinite(p) for p in probabilities)
    ):
        raise ValueError("invalid ECE inputs")
    total = len(probabilities)
    if total == 0:
        raise ValueError("ECE inputs must be non-empty")
    result = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        selected = [i for i, p in enumerate(probabilities) if lo <= p < hi or (b == bins - 1 and p == hi)]
        if selected:
            result += (
                len(selected)
                / total
                * abs(
                    sum(probabilities[i] for i in selected) / len(selected)
                    - sum(correct[i] for i in selected) / len(selected)
                )
            )
    return result


def permute_options(options: list[str], permutation: list[int]) -> list[str]:
    if len(options) != 4 or sorted(permutation) != list(range(len(options))) or len(set(options)) != len(options):
        raise ValueError("options must be four unique strings and permutation must be bijective")
    return [options[i] for i in permutation]


def remap_answer(original_index: int, permutation: list[int]) -> int:
    if not 0 <= original_index < 4 or sorted(permutation) != [0, 1, 2, 3] or original_index not in permutation:
        raise ValueError("answer index or permutation invalid")
    return permutation.index(original_index)


def canonical_item_hash(question: str, options: list[str], answer: int) -> str:
    payload = json.dumps(
        {"question": question, "options": options, "answer": answer}, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def expand_conditions(outcome_items: dict[str, list[str]], generation_seed: int = 20260830) -> list[Condition]:
    conditions: list[Condition] = []
    for outcome, item_ids in sorted(outcome_items.items()):
        for item_id in item_ids:
            baseline_key = f"baseline:{item_id}:{generation_seed}"
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
                conditions.extend(
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
                    for seed in RANDOM_CONTROL_SEEDS
                )
    return conditions


def operation_counts(xstest_items: int, calibration_items: int, consistency_pairs: int) -> dict[str, int]:
    representations = xstest_items + calibration_items + 2 * consistency_pairs
    states = len(ALPHAS) + (len(ALPHAS) - 1) * len(RANDOM_CONTROL_SEEDS)
    logical = representations * states
    return {
        "representations": representations,
        "logical_condition_states": logical,
        "unique_baseline_states": representations,
        "xstest_generations": xstest_items * states,
        "mmlu_option_scoring_operations": calibration_items * states * 4,
        "consistency_original_scoring_operations": consistency_pairs * states * 4,
        "consistency_transformed_scoring_operations": consistency_pairs * states * 4,
        "total_forward_operation_estimate": xstest_items * states
        + calibration_items * states * 4
        + consistency_pairs * states * 8,
    }


def _cache_root() -> Path:
    return (
        Path(os.environ.get("USERPROFILE", str(Path.home())))
        / ".cache"
        / "alignmentdelta"
        / "source_data"
        / "mmlu"
        / CACHE_REVISION
    )


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_materialized_data(root: Path) -> dict[str, Any]:
    manifest_dir = root / "configs" / "manifests"
    mmlu = tomllib.loads((manifest_dir / "mmlu.toml").read_text(encoding="utf-8"))
    cal_manifest = tomllib.loads((manifest_dir / "mmlu_exploratory_pilot.toml").read_text(encoding="utf-8"))
    con_manifest = tomllib.loads((manifest_dir / "consistency_pairs.toml").read_text(encoding="utf-8"))
    cache = _cache_root()
    if mmlu.get("revision") != CACHE_REVISION or mmlu.get("source_class") != "provenance_verified_mirror":
        raise ValueError("MMLU source revision/classification is not frozen")
    files = _load_json(manifest_dir / "mmlu_source_files.json")
    for item in files:
        p = cache / item["path"]
        if (
            not p.exists()
            or p.stat().st_size != item["bytes"]
            or hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]
        ):
            raise ValueError(f"source file hash/size mismatch: {item['path']}")
    cal = _load_json(cache / "calibration_items.json")
    pairs = _load_json(cache / "consistency_pairs.json")
    cal_ids = [x["stable_id"] for x in cal]
    pair_ids = [x["pair_id"] for x in pairs]
    if cal_ids != cal_manifest["ids"] or pair_ids != con_manifest["pair_ids"] or cal_ids != mmlu["pilot_ids"]:
        raise ValueError("tracked and cached subset IDs differ")
    source_ids = [x["source_id"] for x in pairs]
    if set(cal_ids) & set(source_ids) or len(cal_ids) != 12 or len(pairs) != 12:
        raise ValueError("calibration/consistency disjointness or size failed")
    for p in pairs:
        if sorted(p["permutation"]) != [0, 1, 2, 3] or len(p["source_options"]) != 4 or len(p["variant_options"]) != 4:
            raise ValueError(f"invalid consistency pair: {p['pair_id']}")
        if p["variant_options"] != permute_options(p["source_options"], p["permutation"]):
            raise ValueError(f"option permutation mismatch: {p['pair_id']}")
        if p["variant_answer"] != remap_answer(p["source_answer"], p["permutation"]):
            raise ValueError(f"answer remapping mismatch: {p['pair_id']}")
        if canonical_item_hash(p["question"], p["variant_options"], p["variant_answer"]) != p["variant_hash"]:
            raise ValueError(f"variant hash mismatch: {p['pair_id']}")
    return {"calibration": cal, "pairs": pairs, "source_files": files}


def _xstest_items(data: dict[str, Any]) -> list[str]:
    ids = list(data.get("safe", {}).get("ids", [])) + list(data.get("unsafe", {}).get("ids", []))
    if (
        len(ids) != 24
        or len(ids) != len(set(ids))
        or data.get("safe", {}).get("count") != 12
        or data.get("unsafe", {}).get("count") != 12
    ):
        raise ValueError("XSTest exploratory subset is not the frozen 12+12 manifest")
    return ids


def dry_run(root: Path) -> int:
    xstest = tomllib.loads((root / "configs/manifests/xstest_exploratory_pilot.toml").read_text(encoding="utf-8"))
    xstest_ids = _xstest_items(xstest)
    data = validate_materialized_data(root)
    pair_ids = [p["pair_id"] for p in data["pairs"]]
    counts = operation_counts(len(xstest_ids), len(data["calibration"]), len(pair_ids))
    consistency_representations = [f"{pair_id}:original" for pair_id in pair_ids] + [
        f"{pair_id}:transformed" for pair_id in pair_ids
    ]
    conditions = expand_conditions(
        {
            "xstest_generation": xstest_ids,
            "mmlu_option_scoring": [x["stable_id"] for x in data["calibration"]],
            "consistency": consistency_representations,
        }
    )
    if (
        len({c.baseline_reference for c in conditions}) != counts["unique_baseline_states"]
        or len(conditions) != counts["logical_condition_states"]
    ):
        raise ValueError("condition expansion or baseline deduplication failed")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(f"model: {MODEL_ID}@{MODEL_REVISION}")
    print("xstest_items: 24")
    print("mmlu_calibration_items: 12")
    print("consistency_pairs: 12")
    print("generation_operations: xstest only")
    print("option_scoring_operations: mmlu calibration and both consistency representations")
    print("model_inference: 0")
    print("model_weights_loaded: 0")
    print("decision: EXPLORATORY_PILOT_GO")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--technical-smoke", action="store_true")
    parser.add_argument("--initialize-run", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--task", choices=("xstest", "mmlu", "consistency", "all"), default="all")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/runs/step_4_0"))
    parser.add_argument("--master-run-id")
    parser.add_argument("--chunk-index", type=int, default=0)
    parser.add_argument("--chunk-count", type=int, default=1)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    if args.initialize_run:
        from .production_orchestrator import initialize_master_run

        manifest = initialize_master_run(
            args.output_root.resolve(), repo_root=args.root.resolve(), master_run_id=args.master_run_id
        )
        print(json.dumps(manifest, sort_keys=True))
        return 0
    if args.synthetic:
        from .execution_engine import ExecutionConfig, run_synthetic

        config = ExecutionConfig(
            args.output_root, "synthetic-step4a", args.task, args.chunk_index, args.chunk_count, True
        )
        print(json.dumps(run_synthetic(config, resume=args.resume), sort_keys=True))
        return 0
    if args.execute:
        if args.profile != "cloud_gpu":
            raise SystemExit("real scientific execution requires --profile cloud_gpu")
        from .cloud_adapter import (
            EXPECTED_DIRECTION_SHA256,
            QwenScientificAdapter,
            cloud_preflight,
            load_qwen_model,
            reconstruct_direction,
        )
        from .prepare_cloud_data import hydrate
        from .production_orchestrator import run_production, validate_master_manifest, validate_technical_gate
        from .providers import make_production_provider

        output_root = args.output_root.resolve()
        root = args.root.resolve()
        manifest = validate_master_manifest(output_root, repo_root=root, require_clean=True)
        cloud_preflight(root, args.profile, output_root)
        validate_technical_gate(output_root, manifest)
        cache_root = Path(
            os.environ.get("ALIGNMENTDELTA_CACHE", Path.home() / ".cache" / "alignmentdelta" / "source_data")
        )
        sources = hydrate(cache_root, verify_only=True)
        model, tokenizer, _ = load_qwen_model()
        direction = reconstruct_direction(model, tokenizer, Path(sources["refusal_direction"]["root"]))
        controls = {}
        for seed in RANDOM_CONTROL_SEEDS:
            from alignmentdelta.engineering.controls import orthogonal_control

            controls[seed] = orthogonal_control(direction, seed)[0]
        adapter = QwenScientificAdapter(model, tokenizer=tokenizer)
        provider = make_production_provider(cache_root, root)
        result = run_production(
            output_root,
            repo_root=root,
            adapter=adapter,
            item_provider=provider,
            resume=args.resume,
            technical_state={
                "direction": direction,
                "controls": controls,
                "direction_sha256": EXPECTED_DIRECTION_SHA256,
                "layer": 27,
                "hidden_dimension": 2048,
            },
            task=None if args.task == "all" else args.task,
            chunk_index=args.chunk_index,
            chunk_count=args.chunk_count,
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    if args.technical_smoke:
        if args.profile != "cloud_gpu":
            raise SystemExit("technical smoke requires --profile cloud_gpu")
        from .cloud_adapter import run_cloud_technical_smoke

        cache_root = Path(
            os.environ.get("ALIGNMENTDELTA_CACHE", Path.home() / ".cache" / "alignmentdelta" / "source_data")
        )
        print(
            json.dumps(
                run_cloud_technical_smoke(args.root.resolve(), args.output_root.resolve(), cache_root), sort_keys=True
            )
        )
        return 0
    if not args.dry_run:
        raise SystemExit("safe default: use --dry-run or the explicit --synthetic validation mode")
    return dry_run(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
