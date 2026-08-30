from pathlib import Path

from alignmentdelta.experiments.canonical import experiment_condition_id
from alignmentdelta.experiments.config import load_experiment_config
from alignmentdelta.experiments.ids import new_run_id

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs" / "experiments" / "example.schema.toml"


def test_condition_id_is_deterministic() -> None:
    config = load_experiment_config(CONFIG)
    assert experiment_condition_id(config) == experiment_condition_id(config)


def test_toml_formatting_does_not_change_condition_id(tmp_path: Path) -> None:
    original = CONFIG.read_text(encoding="utf-8")
    reformatted = "\n".join(line.strip() for line in original.splitlines()) + "\n"
    first = load_experiment_config(CONFIG)
    second_path = tmp_path / "reformatted.toml"
    second_path.write_text(reformatted, encoding="utf-8")
    second = load_experiment_config(second_path)
    assert experiment_condition_id(first) == experiment_condition_id(second)


def test_scientific_change_changes_condition_id(tmp_path: Path) -> None:
    changed = CONFIG.read_text(encoding="utf-8").replace("intervention_strength = 0.0", "intervention_strength = 0.5")
    path = tmp_path / "changed.toml"
    path.write_text(changed, encoding="utf-8")
    original_id = experiment_condition_id(load_experiment_config(CONFIG))
    changed_id = experiment_condition_id(load_experiment_config(path))
    assert original_id != changed_id


def test_execution_profile_and_replicate_count_do_not_change_condition_id(tmp_path: Path) -> None:
    changed = (
        CONFIG.read_text(encoding="utf-8")
        .replace('execution_profile = "cpu_test"', 'execution_profile = "cloud_gpu"')
        .replace("planned_replicates = 1", "planned_replicates = 3")
    )
    path = tmp_path / "execution-only-change.toml"
    path.write_text(changed, encoding="utf-8")
    assert experiment_condition_id(load_experiment_config(CONFIG)) == experiment_condition_id(
        load_experiment_config(path)
    )


def test_absent_and_explicit_optional_revisions_are_distinguished(tmp_path: Path) -> None:
    explicit = CONFIG.read_text(encoding="utf-8")
    absent = explicit.replace('revision = "<MODEL_REVISION_OR_NULL>"\n', "")
    absent = absent.replace('tokenizer_revision = "<TOKENIZER_REVISION_OR_NULL>"\n', "")
    explicit_path = tmp_path / "explicit.toml"
    absent_path = tmp_path / "absent.toml"
    explicit_path.write_text(explicit, encoding="utf-8")
    absent_path.write_text(absent, encoding="utf-8")
    assert experiment_condition_id(load_experiment_config(explicit_path)) != experiment_condition_id(
        load_experiment_config(absent_path)
    )


def test_run_ids_are_unique_and_distinct_from_condition_id() -> None:
    first = new_run_id()
    second = new_run_id()
    assert first != second
    assert first.startswith("run-")
    assert "condition-" not in first
