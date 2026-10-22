from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
from contextlib import ExitStack
from pathlib import Path
from urllib.error import HTTPError

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "devtools"
    / "conda-build"
    / "release_route.py"
)
SPEC = importlib.util.spec_from_file_location("sabueso_release_route", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
route = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(route)
SHA = "cd4680a653942c4cace7e8ae89b9cc623242f12c"


def test_committed_release_plan_names_a_version_route_and_all_exact_gates():
    # The committed plan changes with every release; what must hold is its shape.
    # 0.1.0, the first public release, is staged.
    plan = route.read_plan()
    assert re.fullmatch(r"\d+\.\d+\.\d+", plan["version"])
    assert plan["route"] in {"direct", "staged"}
    assert plan["reason"] and plan["decision_by"]
    assert plan["required_workflows"] == [
        ".github/workflows/ci.yml",
        ".github/workflows/moli-governance.yml",
    ]


def _plan(*, chosen_route: str = "direct") -> dict:
    return {
        "version": "0.1.0",
        "route": chosen_route,
        "reason": "No pre-public installed artifact or coupled consumer gate is required.",
        "decision_by": "release maintainer",
        "required_workflows": [route.FULL_MATRIX],
    }


def test_committed_plan_rejects_unset_fields_and_missing_matrix(tmp_path):
    plan = tmp_path / "release_plan.toml"
    plan.write_text(
        'version = ""\nroute = ""\nreason = ""\ndecision_by = ""\n'
        'required_workflows = [".github/workflows/ci.yml"]\n',
        encoding="utf-8",
    )
    with pytest.raises(route.ReleaseRouteError, match="canonical"):
        route.read_plan(plan)
    plan.write_text(
        'version = "0.1.0"\nroute = "direct"\nreason = "routine"\n'
        'decision_by = "maintainer"\nrequired_workflows = []\n',
        encoding="utf-8",
    )
    with pytest.raises(route.ReleaseRouteError, match="full-matrix"):
        route.read_plan(plan)


@pytest.mark.parametrize("wrong_field", ["head_sha", "path", "conclusion", "status"])
def test_required_ci_must_have_exact_identity_and_success(monkeypatch, wrong_field):
    run = {
        "id": 123,
        "head_sha": SHA,
        "path": route.FULL_MATRIX,
        "status": "completed",
        "conclusion": "success",
    }
    wrong_values = {
        "head_sha": "0" * 40,
        "path": ".github/workflows/docs_ci.yaml",
        "conclusion": "failure",
        "status": "in_progress",
    }
    run[wrong_field] = wrong_values[wrong_field]
    monkeypatch.setattr(
        route, "_read_json", lambda *args, **kwargs: {"workflow_runs": [run]}
    )
    with pytest.raises(route.ReleaseRouteError, match="no successful exact-commit run"):
        route.verified_workflow_runs(
            "uibcdf/sabueso", SHA, [route.FULL_MATRIX], "token"
        )


def test_required_ci_accepts_only_exact_successful_run(monkeypatch):
    run = {
        "id": 123,
        "head_sha": SHA,
        "path": route.FULL_MATRIX,
        "status": "completed",
        "conclusion": "success",
    }

    def fake_read(url, *, token=None):
        assert "head_sha=" + SHA in url
        assert token == "token"
        return {"workflow_runs": [run]}

    monkeypatch.setattr(route, "_read_json", fake_read)
    assert route.verified_workflow_runs(
        "uibcdf/sabueso", SHA, [route.FULL_MATRIX], "token"
    ) == [{"workflow": route.FULL_MATRIX, "run_id": 123}]


def test_direct_preflight_accepts_only_explicit_404(monkeypatch):
    with HTTPError("https://example.invalid", 404, "not found", {}, None) as error:

        def absent(url, *, token=None):
            raise error

        monkeypatch.setattr(route, "_read_json", absent)
        assert route.assert_version_unoccupied("0.1.0")["state"] == "absent"
        assert error.closed


@pytest.mark.parametrize("distributions", [[{"basename": "noarch/sabueso-py_0"}], []])
def test_direct_preflight_rejects_any_existing_version(monkeypatch, distributions):
    monkeypatch.setattr(
        route, "_read_json", lambda *args, **kwargs: {"distributions": distributions}
    )
    with pytest.raises(route.ReleaseRouteError, match="direct upload is forbidden"):
        route.assert_version_unoccupied("0.1.0")


def test_direct_preflight_rejects_registry_error(monkeypatch):
    with HTTPError("https://example.invalid", 503, "unavailable", {}, None) as error:

        def unavailable(url, *, token=None):
            raise error

        monkeypatch.setattr(route, "_read_json", unavailable)
        with pytest.raises(route.ReleaseRouteError, match="HTTP 503") as caught:
            route.assert_version_unoccupied("0.1.0")
        assert caught.value.__cause__ is error and error.closed


def test_staged_plan_cannot_enter_the_direct_release_route(monkeypatch, tmp_path):
    monkeypatch.setattr(route, "read_plan", lambda: _plan(chosen_route="staged"))

    def should_not_run(*args, **kwargs):
        raise AssertionError(
            "no gate or registry request is allowed after a route mismatch"
        )

    monkeypatch.setattr(route, "verified_workflow_runs", should_not_run)
    monkeypatch.setattr(route, "assert_version_unoccupied", should_not_run)
    with pytest.raises(route.ReleaseRouteError, match="does not match"):
        route.check_route(
            version="0.1.0",
            route="direct",
            sha=SHA,
            repository="uibcdf/sabueso",
            receipt=tmp_path / "receipt.json",
        )


def test_direct_route_retains_decision_gate_and_preflight(monkeypatch, tmp_path):
    monkeypatch.setattr(route, "read_plan", _plan)
    monkeypatch.setattr(
        route,
        "verified_workflow_runs",
        lambda *args: [{"workflow": route.FULL_MATRIX, "run_id": 123}],
    )
    monkeypatch.setattr(
        route, "assert_version_unoccupied", lambda version: {"state": "absent"}
    )
    monkeypatch.setenv("GH_TOKEN", "token")
    receipt = tmp_path / "receipt.json"
    evidence = route.check_route(
        version="0.1.0",
        route="direct",
        sha=SHA,
        repository="uibcdf/sabueso",
        receipt=receipt,
    )
    assert evidence["candidate_sha"] == SHA
    assert evidence["gates"][0]["run_id"] == 123
    assert evidence["preflight"]["state"] == "absent"
    assert json.loads(receipt.read_text(encoding="utf-8")) == evidence


def test_public_poststate_matches_the_exact_built_file(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(
        json.dumps({"version": "0.1.0", "route": "direct"}), encoding="utf-8"
    )
    package = tmp_path / "sabueso-0.1.0-py_0.tar.bz2"
    package.write_bytes(b"noarch candidate")
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    record = {
        "sha256": digest,
        "channel": route.PUBLIC_CHANNEL,
        "fn": package.name,
        "noarch": "python",
        "url": route.PUBLIC_CHANNEL + "/" + package.name,
    }
    monkeypatch.setattr(
        route.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"sabueso": [record]}), stderr=""
        ),
    )
    evidence = route.verify_public(
        version="0.1.0", built_paths=str(package), receipt=receipt, attempts=1
    )
    assert evidence["public"]["sha256"] == digest
    assert (
        json.loads(receipt.read_text(encoding="utf-8"))["public"]["channel"]
        == route.PUBLIC_CHANNEL
    )


def test_public_poststate_rejects_checksum_mismatch(monkeypatch, tmp_path):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(
        json.dumps({"version": "0.1.0", "route": "direct"}), encoding="utf-8"
    )
    package = tmp_path / "sabueso-0.1.0-py_0.tar.bz2"
    package.write_bytes(b"local candidate")
    record = {
        "sha256": "0" * 64,
        "channel": route.PUBLIC_CHANNEL,
        "fn": package.name,
        "noarch": "python",
    }
    monkeypatch.setattr(
        route.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"sabueso": [record]}), stderr=""
        ),
    )
    with pytest.raises(route.ReleaseRouteError, match="does not match"):
        route.verify_public(
            version="0.1.0", built_paths=str(package), receipt=receipt, attempts=1
        )


# --- immutable coordinates and public poststate (#78) -----------------------------------

_DIGEST = "a" * 64


def _files(*entries):
    """A registry snapshot of the package's files, as api.anaconda.org lists them."""
    return [
        {"basename": basename, "labels": labels, "sha256": sha256}
        for basename, labels, sha256 in entries
    ]


def test_an_absent_coordinate_may_be_uploaded():
    files = _files(("noarch/sabueso-0.4.0-py_0.tar.bz2", ["staging", "main"], _DIGEST))
    state = route.assert_coordinate_unoccupied(files, "0.5.0", 0)
    assert state == {
        "coordinate": "noarch/sabueso-0.5.0-py_0.tar.bz2",
        "state": "absent",
    }


@pytest.mark.parametrize("labels", [["staging"], ["main"], ["staging", "main"], []])
def test_an_occupied_coordinate_is_refused_under_any_label(labels):
    files = _files(("noarch/sabueso-0.5.0-py_0.tar.bz2", labels, _DIGEST))
    with pytest.raises(route.ReleaseRouteError, match="never overwrite"):
        route.assert_coordinate_unoccupied(files, "0.5.0", 0)
    # Another build number is another coordinate.
    route.assert_coordinate_unoccupied(files, "0.5.0", 1)


def test_the_public_poststate_needs_the_main_label_and_the_tested_bytes():
    basename = "noarch/sabueso-0.5.0-py_0.tar.bz2"
    ok = _files((basename, ["staging", "main"], _DIGEST))
    assert route.check_public_poststate(ok, "0.5.0", 0, _DIGEST)["labels"] == [
        "main",
        "staging",
    ]
    with pytest.raises(route.ReleaseRouteError, match="changed bytes"):
        route.check_public_poststate(ok, "0.5.0", 0, "b" * 64)
    with pytest.raises(route.ReleaseRouteError, match="main label"):
        route.check_public_poststate(
            _files((basename, ["staging"], _DIGEST)), "0.5.0", 0, _DIGEST
        )
    with pytest.raises(route.ReleaseRouteError, match="not in the registry"):
        route.check_public_poststate([], "0.5.0", 0, _DIGEST)


def test_an_unobserved_poststate_stays_unresolved(monkeypatch, tmp_path):
    monkeypatch.setattr(route, "registry_files", lambda: [])
    monkeypatch.setattr(route.time, "sleep", lambda _: None)
    receipt = tmp_path / "poststate.json"
    with pytest.raises(route.ReleaseRouteError, match="unresolved"):
        route.verify_poststate(
            version="0.5.0", build_number=0, sha256=_DIGEST, receipt=receipt, attempts=2
        )
    assert not receipt.exists()


def test_public_poststate_closes_each_http_error_before_waiting(monkeypatch, tmp_path):
    with ExitStack() as owned:
        errors = [
            owned.enter_context(
                HTTPError("https://example.invalid", 503, "down", {}, None)
            )
            for _ in range(2)
        ]
        pending = iter(errors)

        def unavailable():
            raise next(pending)

        def wait(seconds):
            assert seconds == 10 and errors[0].closed

        monkeypatch.setattr(route, "registry_files", unavailable)
        monkeypatch.setattr(route.time, "sleep", wait)
        receipt = tmp_path / "poststate.json"
        with pytest.raises(route.ReleaseRouteError, match="HTTP Error 503"):
            route.verify_poststate(
                version="0.5.0",
                build_number=0,
                sha256=_DIGEST,
                receipt=receipt,
                attempts=2,
            )
        assert not receipt.exists() and all(error.closed for error in errors)


def test_an_observed_poststate_is_recorded(monkeypatch, tmp_path):
    files = _files(("noarch/sabueso-0.5.0-py_0.tar.bz2", ["staging", "main"], _DIGEST))
    monkeypatch.setattr(route, "registry_files", lambda: files)
    receipt = tmp_path / "poststate.json"
    evidence = route.verify_poststate(
        version="0.5.0", build_number=0, sha256=_DIGEST, receipt=receipt
    )
    assert json.loads(receipt.read_text()) == evidence
    assert evidence["schema"] == "sabueso.conda-poststate@1"
