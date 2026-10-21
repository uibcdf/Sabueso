"""Publication guards reject local inputs, changed originals and stale decisions."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "fixture_delivery", Path("tools/fixture_delivery.py")
)
delivery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delivery)


@pytest.fixture
def checkout(tmp_path):
    def git(*args):
        return subprocess.run(
            ["git", "-C", str(tmp_path), *args], check=True, capture_output=True
        )

    git("init")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        "Synthetic test base",
    )
    catalog = tmp_path / "sabueso/resolver/source_catalog.json"
    catalog.parent.mkdir(parents=True)
    terms = {
        "licence": "CC0-1.0",
        "reviewed": "2026-10-08",
        "statement": "https://example.invalid/terms",
    }
    catalog.write_text(
        json.dumps({"resources": [{"id": "example", "terms": terms}]}),
        encoding="utf-8",
        newline="",
    )
    original = b"synthetic parser input, not an external response\n"
    path = tmp_path / "temp_data/example/original.txt"
    path.parent.mkdir(parents=True)
    path.write_bytes(original)
    row = {
        "path": "temp_data/example/original.txt",
        "source_id": "example",
        "sha256": hashlib.sha256(original).hexdigest(),
        "bytes": len(original),
        "delivery": "local_only",
        "recorded_licence": "CC0-1.0",
        "reviewed": terms["reviewed"],
        "statement": terms["statement"],
        "terms_sha256": hashlib.sha256(
            json.dumps(
                terms, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ).hexdigest(),
        "basis": "Synthetic local-only decision for guard testing.",
    }
    manifest = tmp_path / delivery.MANIFEST
    manifest.parent.mkdir(parents=True)
    data = {
        "format": "sabueso.fixture_delivery@1",
        "files": [row],
        "local_qualification_tests": {},
    }
    manifest.write_text(json.dumps(data), encoding="utf-8", newline="")
    (tmp_path / ".gitignore").write_text(
        "/temp_data/example/\n", encoding="utf-8", newline=""
    )
    return tmp_path, path, manifest, data, git


def test_local_originals_can_be_absent_from_public_checkout_but_not_local_qualification(
    checkout,
):
    root, path, _, _, _ = checkout
    assert delivery.problems(root, local_inputs=True) == []
    path.unlink()
    assert delivery.problems(root) == []
    assert any("missing" in p for p in delivery.problems(root, local_inputs=True))


def test_forced_git_add_of_a_local_original_is_rejected(checkout):
    root, _, _, _, git = checkout
    git("add", "--force", "temp_data/example/original.txt")
    assert any("Git index" in p for p in delivery.problems(root))


def test_removing_ignore_protection_is_rejected_before_staging(checkout):
    root, _, _, _, _ = checkout
    (root / ".gitignore").write_text("", encoding="utf-8", newline="")
    assert any("not protected" in p for p in delivery.problems(root))


def test_changed_original_cannot_reuse_its_qualification(checkout):
    root, path, _, _, _ = checkout
    path.write_bytes(path.read_bytes() + b"changed")
    assert any("original bytes changed" in p for p in delivery.problems(root))


@pytest.mark.parametrize(
    "changed", [{"licence": "NOT-STATED"}, {"caveats": ["New input restriction"]}]
)
def test_terms_changes_require_review_instead_of_automatic_publication(
    checkout, changed
):
    root, _, _, _, _ = checkout
    catalog = root / "sabueso/resolver/source_catalog.json"
    data = json.loads(catalog.read_text(encoding="utf-8"))
    data["resources"][0]["terms"].update(changed)
    catalog.write_text(json.dumps(data), encoding="utf-8", newline="")
    assert any("source terms changed" in p for p in delivery.problems(root))


def test_unreviewed_new_input_and_external_path_are_rejected(checkout):
    root, _, manifest, data, _ = checkout
    (root / "temp_data/unreviewed.json").write_text("{}", encoding="utf-8", newline="")
    assert any("no reviewed delivery" in p for p in delivery.problems(root))
    data["files"][0]["path"] = "../external.txt"
    manifest.write_text(json.dumps(data), encoding="utf-8", newline="")
    assert any("contained temp_data" in p for p in delivery.problems(root))


def test_repository_delivery_requires_the_reviewed_bytes(checkout):
    root, path, manifest, data, _ = checkout
    data["files"][0]["delivery"] = "repository"
    manifest.write_text(json.dumps(data), encoding="utf-8", newline="")
    assert delivery.problems(root) == []
    path.unlink()
    assert any("missing" in p for p in delivery.problems(root))


def test_utf8_source_terms_do_not_depend_on_windows_default_encoding(
    checkout, monkeypatch
):
    root, _, manifest, data, _ = checkout
    catalog = root / "sabueso/resolver/source_catalog.json"
    contents = json.loads(catalog.read_text(encoding="utf-8"))
    terms = contents["resources"][0]["terms"]
    terms["attribution"] = "Müller et al. — original provider"
    data["files"][0]["terms_sha256"] = hashlib.sha256(
        json.dumps(
            terms, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()
    catalog.write_text(json.dumps(contents, ensure_ascii=False), encoding="utf-8")
    manifest.write_text(json.dumps(data), encoding="utf-8")
    original_open = Path.open

    def windows_open(
        path, mode="r", buffering=-1, encoding=None, errors=None, newline=None
    ):
        if "b" not in mode and encoding in (None, "locale"):
            encoding = "cp1252"
        return original_open(path, mode, buffering, encoding, errors, newline)

    monkeypatch.setattr(Path, "open", windows_open)
    assert delivery.problems(root, local_inputs=True) == []


def test_fixture_checkout_preserves_original_bytes_with_windows_line_endings(checkout):
    root, path, _, _, git = checkout
    original = path.read_bytes()
    (root / ".gitattributes").write_bytes(Path(".gitattributes").read_bytes())
    git("config", "core.autocrlf", "true")
    git("add", ".gitattributes")
    git("add", "--force", "temp_data/example/original.txt")
    git(
        "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "commit", "-m", "Preserve synthetic response bytes",
    )  # fmt: skip
    path.unlink()
    git("checkout", "--", "temp_data/example/original.txt")
    assert path.read_bytes() == original


def collection_project(checkout):
    root, _, manifest, data, _ = checkout
    (root / "conftest.py").write_text(
        Path("conftest.py").read_text(encoding="utf-8"), encoding="utf-8", newline=""
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_public.py").write_text(
        "def test_public():\n    assert True\n", encoding="utf-8", newline=""
    )
    (tests / "test_local.py").write_text(
        "from pathlib import Path\n"
        "RAW = Path('temp_data/example/original.txt').read_bytes()\n"
        "def test_local():\n    assert RAW.startswith(b'synthetic')\n",
        encoding="utf-8",
        newline="",
    )
    data["local_qualification_tests"] = {"tests/test_local.py": ["example"]}
    manifest.write_text(json.dumps(data), encoding="utf-8", newline="")
    return root


def run_collection(root, *args):
    import sys

    # The child project must not inherit a parent checkout's conftest options.
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--receptor=llm",
            "--confcutdir",
            str(root),
            *args,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=45,
    )


def test_public_collection_never_imports_missing_local_inputs_and_opt_in_fails_clearly(
    checkout,
):
    root = collection_project(checkout)
    checkout[1].unlink()
    public = run_collection(root)
    assert public.returncode == 0, public.stdout + public.stderr
    assert "1 passed" in public.stdout
    local = run_collection(root, "--local-source-inputs")
    assert local.returncode != 0
    assert "original is missing" in local.stdout + local.stderr


def test_local_opt_in_runs_original_regressions_and_rejects_changed_bytes(checkout):
    root = collection_project(checkout)
    local = run_collection(root, "--local-source-inputs")
    assert local.returncode == 0, local.stdout + local.stderr
    assert "2 passed" in local.stdout
    checkout[1].write_text("changed original", encoding="utf-8", newline="")
    changed = run_collection(root, "--local-source-inputs")
    assert changed.returncode != 0
    assert "original digest differs" in changed.stdout + changed.stderr
