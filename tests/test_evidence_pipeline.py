"""Export and evidence partitions must represent the deployed predictor."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from scipy.special import logit

ROOT = Path(__file__).resolve().parents[1]


def _script(name):
    spec = spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_single_graph_export_rejects_multistage_calibrations():
    from tinydcs.surrogate import ZeroInflatedCalibration
    export = _script("05_export_onnx")
    bundle = SimpleNamespace(conformal=ZeroInflatedCalibration(None, None, .1, .95))
    with pytest.raises(TypeError, match="07_export_zero_inflated"):
        export._validate_supported(bundle)


def test_single_graph_host_undoes_sv_transform_for_point_and_bounds():
    export = _script("05_export_onnx")
    metadata = {"kind": "global", "target_transform_n": 10,
                "conformal_q": 0.0}
    result = export._postprocess(logit([.05, .5, .95]), np.empty((3, 0)), metadata)
    for key in ("point", "lower", "upper"):
        assert result[key] == pytest.approx([0, .5, 1])


def test_export_fixtures_recompute_dependent_features():
    export = _script("05_export_onnx")
    from mechanistic.atmosphere import altitude_ft_to_atm
    names = ["altitude_ft", "ambient_pressure_atm", "altitude_time_min",
             "altitude_vo2_mean_lmin", "altitude_vo2_integral_lmin_min"]
    x = export._random_feature_matrix(names, n=20)
    assert x[:, 1] == pytest.approx(altitude_ft_to_atm(x[:, 0]), rel=1e-6)
    assert x[:, 4] == pytest.approx(x[:, 2] * x[:, 3], rel=1e-6)


def test_grouped_partition_keeps_all_durations_of_a_profile_together():
    from scripts.evidence_common import grouped_partition
    df = pd.DataFrame([
        {"altitude": alt, "prebreathing_time": pb, "exercise_level": ex,
         "time_at_altitude": t}
        for alt in range(18000, 23000, 500) for pb in (0, 30)
        for ex in ("Rest", "Heavy") for t in (10, 20, 30)
    ])
    partition, groups = grouped_partition(df, seed=42)
    assigned = [set(groups.iloc[idx]) for idx in partition.values()]
    assert set.union(*assigned) == set(groups)
    assert not any(assigned[i] & assigned[j] for i in range(3) for j in range(i))
    shuffled = df.sample(frac=1, random_state=9).reset_index(drop=True)
    other, other_groups = grouped_partition(shuffled, seed=42)
    assert all(set(groups.iloc[partition[k]]) == set(other_groups.iloc[other[k]])
               for k in partition)


def test_shared_cells_keep_frozen_membership_across_cleaning_policies():
    from scripts.evidence_common import extend_partition, partition_from_ids
    frozen = {"train": ["a", "b"], "cal": ["c"], "test": ["d"]}
    all_ids = ["d", "a", "b", "c"] + [f"new{i}" for i in range(20)]
    extended = extend_partition(all_ids, frozen, seed=42)
    assert all(set(frozen[k]) <= set(extended[k]) for k in frozen)
    df = pd.DataFrame({"cell_id": ["d", "b", "c", "a"]})
    partition = partition_from_ids(df, extended)
    assert partition["test"].tolist() == [0]
    assert partition["cal"].tolist() == [2]
    with pytest.raises(ValueError, match="exactly once"):
        partition_from_ids(df, {"train": ["a", "b"], "cal": ["c"], "test": ["a"]})


@pytest.mark.parametrize("kind", ["global", "mondrian", "zero_inflated"])
def test_actual_onnx_export_checks_final_bounds_and_preserves_release_gate(tmp_path, kind):
    pytest.importorskip("onnxmltools")
    pytest.importorskip("onnxruntime")
    import json

    from click.testing import CliRunner

    from scripts.evidence_common import feasible_feature_matrix
    from tinydcs.surrogate import TrainConfig, train_surrogate

    names = ["altitude_ft", "ambient_pressure_atm", "altitude_time_min", "altitude_fio2"]
    df = pd.DataFrame(feasible_feature_matrix(names, 300), columns=names)
    df["y"] = np.where(df.altitude_time_min < 80, 0., .2+df.altitude_time_min/400)
    kwargs = {"use_zero_inflated": kind == "zero_inflated"}
    if kind == "mondrian":
        kwargs.update(mondrian_feature="altitude_ft", mondrian_band_width=5000., mondrian_band_origin=18000.)
    model, _ = train_surrogate(df, names, "y", config=TrainConfig(n_estimators=10), **kwargs)
    model.metadata = {"schema_version": "accuracy-v3", "quantitative_enabled": False,
                      "model_id": "test-model", "clinical_validation": False}
    source = tmp_path / "model.joblib"
    model.save(str(source))
    if kind == "zero_inflated":
        export = _script("07_export_zero_inflated_onnx")
        output = tmp_path / "zi"
        arguments = ["--input-model", str(source), "--output-dir", str(output), "--benchmark-n", "32"]
        summary_path = output / "benchmark.json"
    else:
        export = _script("05_export_onnx")
        output = tmp_path / "model.onnx"
        arguments = ["--input-model", str(source), "--output-onnx", str(output), "--benchmark-n", "32"]
        summary_path = output.with_suffix(".onnx.benchmark.json")
    result = CliRunner().invoke(export.main, arguments)
    assert result.exit_code == 0, result.output + repr(result.exception)
    summary = json.loads(summary_path.read_text())
    assert summary["parity"]["support_gate_identical"]
    assert summary["parity"]["quantitative_output_n"] == 0
    assert summary["metadata"]["evidence"]["quantitative_enabled"] is False
