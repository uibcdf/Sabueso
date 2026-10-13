"""Independent comparative readers preserve original explanations and exact pins."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/comparative_support.py").resolve()
DATA = Path("temp_data").resolve()


def invoke(action, output, *, legacy=False, unobserved=False):
    command = [sys.executable, str(SCRIPT)]
    if action == "read":
        command = [sys.executable, "-c", """
import runpy, sys
from pathlib import Path
import ackredit, sabueso
from sabueso.core.card import Card
from sabueso.core import attribution
def forbidden(*args, **kwargs):
    raise RuntimeError('Independent reader cannot acquire, derive or generate credit')
ackredit.register_item = ackredit.track_item = forbidden
attribution._load_backend = forbidden
sabueso.resolve = forbidden
for name in ('sequence_differences', 'variant_tissue_usage', 'isoform_tissue_usage',
             'explain_sequence_differences', 'explain_variant_tissue_usage',
             'explain_isoform_tissue_usage', 'explain', 'knowledge_state'):
    setattr(Card, name, forbidden)
sabueso.__version__ = '999.reader'
script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
runpy.run_path(script, run_name='__main__')
""", str(SCRIPT)]  # fmt: skip
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [*command, action, *(["--legacy"] if legacy else []), *(["--unobserved"] if unobserved else []), "--output", str(output), "--fixtures",
         str(DATA if action != "read" else output / "no-fixtures")],
        cwd=output.parent, env=env, capture_output=True, text=True,
        timeout=120, check=False,
    )  # fmt: skip


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=["historical", "unobserved", "current"])
def bundle(tmp_path_factory, request):
    if request.param == "current":
        return request.getfixturevalue("current_bundle")
    output = tmp_path_factory.mktemp("comparative-support") / "bundle"
    for action in ("produce", "read", "reacquire", "read"):
        result = invoke(
            action,
            output,
            legacy=request.param == "historical",
            unobserved=request.param == "unobserved",
        )
        assert result.returncode == 0, result.stdout + result.stderr
    return output


@pytest.fixture(scope="module")
def current_bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("observed-comparative-support") / "bundle"
    original = {}
    for action in ("produce", "read", "reacquire", "read"):
        result = invoke(action, output)
        assert result.returncode == 0, result.stdout + result.stderr
        if action == "read":
            current = {p.name: p.read_bytes() for p in output.glob("original.*")}
            if original:
                assert current == original
            original = current
    assert (
        load(output / "original.manifest.json")["format"]
        == "sabueso.comparative_support_example@3"
    )
    return output


def test_reader_retains_original_rules_source_versions_and_history_without_recomputation(
    bundle,
):
    original = load(bundle / "original.manifest.json")
    later = load(bundle / "later.manifest.json")
    assert all(original["cards"][r] != later["cards"][r] for r in original["cards"])
    for stage in ("original", "later"):
        report = load(bundle / f"{stage}.report.json")
        reader = load(bundle / f"{stage}.reader.json")
        assert (
            reader["original_report"] == report and reader["observed_acquisitions"] == 0
        )
        assert report["sequence"]["view"]["differences"]
        assert len(report["variants"]["items"]) == 15
        assert len(report["isoforms"]["items"]) == 3
        observed = original["format"] == "sabueso.comparative_support_example@3"
        assert report["execution_observation"]["status"] == (
            "observed" if observed else "not_observed"
        )
        for key in ("sequence", "variants", "isoforms"):
            assert report[key]["rule"]["sabueso_version"] != "999.reader"
        if observed:
            runtime = load(bundle / f"{stage}.runtime.json")
            assert len(runtime["operations"]) == 3 and runtime["acquisitions"]
            assert reader["original_runtime"] == runtime
            assert reader["observed_operations"] == 0
            assert len(load(bundle / f"{stage}.references.csl.json")) >= 4
            assert "@" in (bundle / f"{stage}.references.bib").read_text()
        else:
            assert not (bundle / f"{stage}.runtime.json").exists()


def test_workflow_preserves_each_original_execution_and_source_credit(bundle):
    if (
        load(bundle / "original.manifest.json")["format"]
        != "sabueso.comparative_support_example@3"
    ):
        assert all(
            load(bundle / f"{stage}.report.json")["execution_observation"]["status"]
            == "not_observed"
            for stage in ("original", "later")
        )
        return
    ids = []
    for stage in ("original", "later"):
        report = load(bundle / f"{stage}.report.json")
        runtime = load(bundle / f"{stage}.runtime.json")
        ids.extend(record["execution_id"] for record in runtime["operations"])
        for key, record in zip(
            ("sequence", "variants", "isoforms"), runtime["operations"], strict=True
        ):
            assert report["views"][key] == report[key]["view"]
            assert record["rule"] == report[key]["view"]["rule"]
            assert record["producer"]["version"] != "999.reader"
            assert record["acquisition"] == "not_performed"
            assert (
                record["bibliography_gaps"]
                if key != "sequence"
                else not record["bibliography_gaps"]
            )
        for field in ("items", "uses"):
            expected = {
                json.dumps(row, sort_keys=True)
                for record in runtime["acquisitions"] + runtime["operations"]
                for row in (record["provider"].get("attribution") or {}).get(field, [])
            }
            actual = {
                json.dumps(row, sort_keys=True) for row in runtime["workflow"][field]
            }
            assert actual == expected
    assert len(set(ids)) == 6
    isoform = load(bundle / "original.runtime.json")["operations"][2]
    assert isoform["support_status"] == "partial"
    assert isoform["support_gaps"][0]["reason"] == "input_not_stated"
    assert not any(
        use["field_path"] == "annotations.tissue_specificity"
        for resource in isoform["resources"]
        for use in resource["uses"]
    )


@pytest.mark.parametrize(
    "defect",
    [
        "digest",
        "report_binding",
        "duplicate_execution",
        "execution_time",
        "result",
        "views",
        "parameters",
        "applied_rules",
        "pin",
        "field_support",
        "resource_version",
        "resource_time",
        "credit",
        "bibliography",
        "workflow_missing",
        "workflow_extra",
        "provider",
        "missing_sidecar",
        "gap",
        "stage",
        "membership",
        "producer",
        "extra_view",
        "support_rule_version",
        "resource_item_version",
        "method_scope",
        "method_citation",
    ],
)
def test_reader_refuses_missing_or_misbound_runtime_even_after_rehashing(
    current_bundle, tmp_path, defect
):
    output = tmp_path / "copy"
    shutil.copytree(current_bundle, output)
    runtime_path = output / "original.runtime.json"
    report_path = output / "original.report.json"
    manifest_path = output / "original.manifest.json"
    runtime, report, manifest = (
        load(runtime_path),
        load(report_path),
        load(manifest_path),
    )
    record = runtime["operations"][0]
    if defect == "report_binding":
        runtime["report_sha256"] = "forged"
    elif defect == "duplicate_execution":
        runtime["operations"][1]["execution_id"] = record["execution_id"]
    elif defect == "execution_time":
        record["started_at"] = "2999-01-01T00:00:00+00:00"
    elif defect == "result":
        record["result_id"] = "forged"
    elif defect == "views":
        report["views"]["variants"]["items"][0]["variant"] = "forged"
    elif defect == "extra_view":
        report["views"]["unobserved"] = report["sequence"]["view"]
    elif defect == "parameters":
        runtime["operations"][1]["parameters"]["threshold"] = 0.9
    elif defect == "applied_rules":
        runtime["operations"][1]["applied_rules"].pop()
    elif defect == "pin":
        record["inputs"][0]["card_ref"] = manifest["cards"]["human"]
    elif defect == "field_support":
        record["inputs"][0]["fields"][0]["source_assertion_refs"] = []
    elif defect == "resource_version":
        record["resources"][0]["source"]["version"] = "forged"
    elif defect == "support_rule_version":
        record["support_rule"]["sabueso_version"] = "forged"
    elif defect == "resource_item_version":
        identifier = record["resources"][0]["id"]
        for item in (
            record["provider"]["attribution"]["items"] + runtime["workflow"]["items"]
        ):
            if item["id"] == identifier:
                item["version"] = "forged"
    elif defect in {"method_scope", "method_citation"}:
        method_record = runtime["operations"][1]
        resource = next(
            r
            for r in method_record["resources"]
            if r.get("method_description_citation_ids")
        )
        if defect == "method_scope":
            usage = next(u for u in resource["uses"] if u.get("method_reference_scope"))
            usage["method_reference_scope"]["method_execution"] = "performed"
        else:
            resource["method_description_citation_ids"] = [
                method_record["bibliography"][0]["id"]
            ]
    elif defect == "resource_time":
        record["resources"][0]["uses"][0]["retrieved_at"] = "forged"
    elif defect == "credit":
        record["provider"]["attribution"]["uses"][0]["context"]["execution_id"] = (
            "forged"
        )
    elif defect == "bibliography":
        record["bibliography"][0]["title"] = "forged"
    elif defect == "workflow_missing":
        runtime["workflow"]["uses"].pop()
    elif defect == "workflow_extra":
        use = json.loads(json.dumps(runtime["workflow"]["uses"][0]))
        use["context"]["unexpected_credit"] = True
        runtime["workflow"]["uses"].append(use)
    elif defect == "provider":
        record["provider"]["status"] = "unavailable"
    elif defect == "gap":
        runtime["operations"][2]["support_gaps"] = []
        runtime["operations"][2]["support_status"] = "available"
    elif defect == "stage":
        runtime["stage"] = "later"
    elif defect == "membership":
        del manifest["files"][runtime_path.name]
    else:
        runtime["producer"]["sabueso"] = "forged"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    manifest["files"][report_path.name] = hashlib.sha256(
        report_path.read_bytes()
    ).hexdigest()
    if defect != "report_binding":
        runtime["report_sha256"] = manifest["files"][report_path.name]
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
    if defect == "missing_sidecar":
        runtime_path.unlink()
    elif defect not in ("digest", "membership"):
        manifest["files"][runtime_path.name] = hashlib.sha256(
            runtime_path.read_bytes()
        ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (output / "original.reader.json").unlink()
    result = invoke("read", output)
    assert result.returncode == 2 and "FAIL:" in result.stderr, (
        result.stdout + result.stderr
    )
    assert not (output / "original.reader.json").exists()


def test_reacquired_runtime_cannot_reuse_an_original_execution_identity(
    current_bundle, tmp_path
):
    output = tmp_path / "copy"
    shutil.copytree(current_bundle, output)
    original = load(output / "original.runtime.json")
    runtime_path = output / "later.runtime.json"
    runtime = load(runtime_path)
    record = runtime["operations"][0]
    old = record["execution_id"]
    record["execution_id"] = original["operations"][0]["execution_id"]
    for use in record["provider"]["attribution"]["uses"] + runtime["workflow"]["uses"]:
        if use["context"].get("execution_id") == old:
            use["context"]["execution_id"] = record["execution_id"]
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
    manifest_path = output / "later.manifest.json"
    manifest = load(manifest_path)
    manifest["files"][runtime_path.name] = hashlib.sha256(
        runtime_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (output / "later.reader.json").unlink()
    result = invoke("read", output)
    assert result.returncode == 2 and "Reacquisition reused" in result.stderr, (
        result.stdout + result.stderr
    )
    assert not (output / "later.reader.json").exists()


@pytest.mark.parametrize(
    "defect",
    ["digest", "role", "field", "assertion", "time", "locator", "rule", "parameters"],
)
def test_reader_refuses_changed_or_misbound_original_inputs_even_with_new_report_digest(
    bundle, tmp_path, defect
):
    output = tmp_path / "copy"
    shutil.copytree(bundle, output)
    filename = "original.report.json"
    report_path = output / filename
    report = load(report_path)
    manifest_path = output / "original.manifest.json"
    manifest = load(manifest_path)
    if defect == "role":
        report["sequence"]["card_refs"][0] = manifest["cards"]["human"]
    elif defect == "field":
        report["sequence"]["fields"][0]["node"]["value"] = "forged"
    elif defect in ("assertion", "time"):
        row = report["sequence"]["fields"][0]["source_assertions"][0]
        row["asserted_value" if defect == "assertion" else "retrieved_at"] = "forged"
    elif defect == "locator":
        report["variants"]["items"][0]["variant_input"]["locator"]["index"] = 999
    elif defect == "rule":
        report["isoforms"]["view"]["rule"]["rule"] = "isoform_exon_usage@999"
    elif defect == "parameters":
        report["variants"]["rule"]["parameters"]["threshold"] = 0.9
    else:
        report["cards"]["human"] = "forged"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    if defect != "digest":
        manifest["files"][filename] = hashlib.sha256(
            report_path.read_bytes()
        ).hexdigest()
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (output / "original.reader.json").unlink()
    result = invoke("read", output)
    assert result.returncode == 2 and "FAIL:" in result.stderr, (
        result.stdout + result.stderr
    )
    assert not (output / "original.reader.json").exists()


def test_completed_producer_stages_cannot_be_overwritten(bundle):
    original = (bundle / "original.manifest.json").read_bytes()
    for action in ("produce", "reacquire"):
        result = invoke(action, bundle)
        assert result.returncode == 2
    assert (bundle / "original.manifest.json").read_bytes() == original
