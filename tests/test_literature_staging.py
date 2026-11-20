from tinydcs.literature_staging import digest, json_bytes, project, stage_report


REVISION = "a" * 40
REPORT = {
    "report_id": "fixture-1", "source_sha256": "b" * 64, "physical_pages": [1, 2],
    "observations": [{
        "stratum_id": "sample-a", "cohort_id": "fictional-1", "setting": "chamber",
        "endpoint": "clinical_dcs", "endpoint_definition": "Synthetic case definition",
        "ascertainment": "Synthetic ascertainment", "numerator": 0, "denominator": 20,
        "denominator_unit": "exposures", "overlap": "unknown", "physical_page": 2,
        "provenance_locator": "Table 1", "review_status": "source_verified",
    }],
}


def test_source_review_is_not_release():
    review, model = stage_report(REPORT)
    obs = review["observations"][0]
    assert obs["numerator"] == 0 and not obs["validation_errors"] and not obs["missing_fields"]
    assert review["eligibility"] == "pending"
    assert "cohort_independence_unresolved" in model["observations"][0]["model_blockers"]
    assert model["training_release"] == "withheld"


def test_reject_rounded_integer_and_unverified_page():
    invalid = {**REPORT["observations"][0], "rounded_rate_only": True, "numerator": 23,
               "physical_page": 3, "review_status": "pending"}
    review, _ = stage_report({**REPORT, "observations": [invalid, invalid]})
    assert set(review["observations"][0]["validation_errors"]) == {
        "integer_numerator_requires_source_evidence", "numerator_exceeds_denominator",
        "physical_page_outside_verified_source_range", "requires_primary_source_review",
    }
    assert "duplicate_observation_identity_in_report" in review["observations"][1]["validation_errors"]


def test_dry_run_and_deterministic_write(tmp_path):
    output = tmp_path / "stage"
    manifest = {"repo_revision": REVISION, "reports": [REPORT]}
    result = project(manifest, output, dry_run=True)
    assert not output.exists() and result["manifest_sha256"] == digest(json_bytes(manifest))
    first = project(manifest, output, dry_run=False)
    second = project(manifest, output, dry_run=False)
    assert first == second
    assert (output / "systematic-review-staging.json").is_file()
    assert (output / "clinical-model-staging.json").is_file()
