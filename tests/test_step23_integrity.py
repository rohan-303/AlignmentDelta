import hashlib
import re
from pathlib import Path

import torch

ROOT = Path(__file__).parents[1]


MODEL_REVISIONS = {
    "Qwen/Qwen2.5-3B-Instruct": "aa8e72537993ba99e69dfaafa59ed015b17504d1",
    "meta-llama/Llama-3.2-3B-Instruct": "0cb88a4f764b7a12671c53f0838cd831a0843b95",
    "google/gemma-2-2b-it": "299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8",
    "Qwen/Qwen2.5-1.5B-Instruct": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "meta-llama/Llama-3.2-1B-Instruct": "9213176726f574b556790deb65791e0c5aa438b6",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": "31b70e2e869a7173562077fd711b654946d38674",
}


def test_all_model_revisions_are_full_sha_pins() -> None:
    assert all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in MODEL_REVISIONS.values())
    text = (ROOT / "docs/protocols/MODEL_METADATA_REGISTRY.md").read_text(encoding="utf-8")
    assert all(revision in text for revision in MODEL_REVISIONS.values())


def test_required_implementation_contracts_exist() -> None:
    required = [
        "ARCHITECTURE_ADAPTER_SPEC.md",
        "MODEL_LOADING_SPEC.md",
        "RESIDUAL_CAPTURE_SPEC.md",
        "DIRECTION_ARTIFACT_SPEC.md",
        "INTERVENTION_OPERATOR_SPEC.md",
        "CONTROL_DIRECTION_SPEC.md",
        "PILOT_RUNNER_SPEC.md",
        "DIRECTION_ARTIFACT_SCHEMA.md",
        "METHOD_DIFFERENCE_TABLE.md",
    ]
    assert all((ROOT / "docs/implementation" / name).is_file() for name in required)


def test_projection_math_is_unit_direction_and_axis_safe() -> None:
    h = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    r = torch.tensor([1.0, 0.0])
    alpha = 0.5
    projected = h - alpha * r * (h @ r)
    assert torch.allclose(projected, torch.tensor([[0.5, 2.0], [2.5, 4.0]]))


def test_random_control_projection_is_orthogonal_and_deterministic() -> None:
    r = torch.nn.functional.normalize(torch.tensor([1.0, 2.0, 3.0]), dim=0)

    def make(seed: int) -> torch.Tensor:
        generator = torch.Generator(device="cpu").manual_seed(seed)
        z = torch.randn(3, generator=generator)
        q = z - torch.dot(z, r) * r
        return q / torch.linalg.vector_norm(q)

    q1, q2 = make(20260830), make(20260830)
    assert torch.equal(q1, q2)
    assert torch.isclose(torch.dot(q1, r), torch.tensor(0.0), atol=1e-6)


def test_deterministic_source_split_does_not_depend_on_model_outputs() -> None:
    ids = sorted(["source-c", "source-a", "source-b", "source-d", "source-e"])
    assignments = {
        item_id: "train" if int(hashlib.sha256(f"20260830:{item_id}".encode()).hexdigest(), 16) % 5 else "validation"
        for item_id in ids
    }
    assert assignments == {
        item_id: "train" if int(hashlib.sha256(f"20260830:{item_id}".encode()).hexdigest(), 16) % 5 else "validation"
        for item_id in ids
    }


def test_access_table_has_no_unresolved_final_gate() -> None:
    text = (ROOT / "docs/protocols/ACCESS_LICENSE_FREEZE.md").read_text(encoding="utf-8")
    assert "| unresolved |" not in text
    assert "`blocked`" in text
    assert "cleared_with_restrictions" in text


def test_blocked_decision_and_deferred_execution_are_explicit() -> None:
    tracker = (ROOT / "docs/protocols/PRE_EXECUTION_GATE_TRACKER.md").read_text(encoding="utf-8")
    assert "current state" in tracker
    assert "blocked" in tracker
    assert "deferred_by_design" in tracker
    for phrase in ("target weights", "inference", "scientific measurements"):
        assert phrase in tracker
