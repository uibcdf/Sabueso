"""Caller-selected diagnostic restrictions at Sabueso-owned error construction (#150)."""

import importlib
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import smonitor

import sabueso
from sabueso.core.errors import ArgumentError


class Opaque:
    def __repr__(self):
        raise AssertionError("diagnostic repr collected")

    def __str__(self):
        raise AssertionError("diagnostic str collected")


@pytest.mark.parametrize(
    "boundary", ["constructor", "structures", "boolean", "paths", "options"]
)
def test_restricted_argument_errors_do_not_construct_value_text(boundary):
    from sabueso._private.argdigest import _shared

    with smonitor.diagnostic_scope():
        with pytest.raises(ArgumentError) as caught:
            if boundary == "constructor":
                raise ArgumentError(
                    argument="fixture", value=Opaque(), reason="invalid"
                )
            elif boundary == "structures":
                sabueso.resolve_protein_card("P60174", structures=Opaque())
            elif boundary == "boolean":
                sabueso.resolve_protein_card("P60174", ligand_sites=Opaque())
            elif boundary == "paths":
                _shared.path_list("fields", [Opaque()], "fixture")
            else:
                _shared.options(
                    "options", {Opaque(): 1}, "fixture", {"allowed": lambda x: None}
                )
        assert caught.value.code == "SABUESO-E-ARG-001"
        assert isinstance(caught.value, ValueError)


@pytest.mark.parametrize("boundary", ["knowledge_query", "thresholds"])
def test_restricted_digester_error_translation_does_not_stringify_native_error(
    monkeypatch, boundary
):
    from sabueso.core.packets import KnowledgeQuery

    class NativeArgumentError(ArgumentError):
        def __str__(self):
            raise AssertionError("native diagnostic str collected")

    native = NativeArgumentError("synthetic native failure")

    def failed(*args, **kwargs):
        raise native

    module = importlib.import_module("sabueso._private.argdigest.argument." + boundary)
    if boundary == "knowledge_query":
        monkeypatch.setattr(KnowledgeQuery, "from_dict", failed)

        def call():
            return module.digest_knowledge_query({"invalid": True}, caller="fixture")
    else:
        monkeypatch.setattr("sabueso.core.bioactivities.resolve_thresholds", failed)

        def call():
            return module.digest_thresholds({"invalid": True}, caller="fixture")

    with smonitor.diagnostic_scope():
        with pytest.raises(ArgumentError) as caught:
            call()
    assert caught.value is not native
    if boundary == "knowledge_query":
        assert caught.value.__cause__ is native


def test_detailed_error_text_and_legacy_capability_absence_remain_compatible(
    monkeypatch,
):
    expected = "Argument 'fixture' of caller cannot take 3: invalid."
    error = ArgumentError(
        argument="fixture", value=3, caller="caller", reason="invalid"
    )
    assert error.raw_message == expected
    detailed = str(error)
    monkeypatch.delattr(smonitor, "get_capture_policy")
    assert (
        str(
            ArgumentError(
                argument="fixture", value=3, caller="caller", reason="invalid"
            )
        )
        == detailed
    )


@pytest.mark.parametrize("permission", ["arguments", "exception_text"])
def test_partial_capture_permissions_prevent_argument_error_payload_construction(
    permission,
):
    with smonitor.diagnostic_scope(smonitor.CapturePolicy(**{permission: False})):
        error = ArgumentError(argument="fixture", value=Opaque(), reason="invalid")
    assert error.code == "SABUESO-E-ARG-001"


def test_restricted_unknown_threshold_does_not_format_the_native_key():
    from sabueso._private.argdigest.argument.thresholds import digest_thresholds

    with smonitor.diagnostic_scope():
        with pytest.raises(ArgumentError):
            digest_thresholds({Opaque(): 1}, caller="fixture")


def fresh(tmp_path, script, *arguments):
    result = subprocess.run(
        [sys.executable, "-B", "-c", textwrap.dedent(script), *arguments],
        cwd=tmp_path,
        env={
            **os.environ,
            "PYTHONPATH": str(Path(sabueso.__file__).resolve().parent.parent),
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "setup", ["unconfigured", "application", "application_empty", "project"]
)
def test_import_reload_first_use_and_real_emission_preserve_selected_setup(
    tmp_path, setup
):
    fresh(
        tmp_path,
        """
        import importlib, logging, sys, warnings
        from pathlib import Path
        import smonitor
        from smonitor.handlers.memory import MemoryHandler
        manager = smonitor.get_manager()
        setup = sys.argv[1]
        sink = MemoryHandler()
        if setup in ("application", "application_empty"):
            smonitor.configure(handlers=[sink] if setup=="application" else [], profile="qa", level="DEBUG",
                capture_warnings=False, capture_logging=False, capture_exceptions=False,
                routes=[], filters=[], run_id="application-run")
        elif setup == "project":
            Path('_smonitor.py').write_text(
                'SMONITOR = {"profile": "qa", "level": "CRITICAL", '
                '"capture_warnings": False, "capture_logging": False, '
                '"capture_exceptions": False}\\n')
        before = manager.config, manager._policy, tuple(manager._handlers)
        hooks = warnings.showwarning, sys.excepthook, tuple(logging.root.handlers)
        import sabueso
        from sabueso._private.smonitor.outcomes import report_outcomes
        selected = manager.config, manager._policy, tuple(manager._handlers)
        selected_hooks = warnings.showwarning, sys.excepthook, tuple(logging.root.handlers)
        importlib.reload(sabueso)
        for _ in range(2):
            with warnings.catch_warnings(record=True) as seen:
                warnings.simplefilter('always')
                report_outcomes([{'source':'fixture','status':'error','detail':'synthetic detail'}],
                                subject='fixture')
                assert len(seen) == 1
        assert manager.config is selected[0] and manager._policy is selected[1]
        if setup != 'application_empty':
            assert tuple(manager._handlers) == selected[2]
        assert selected_hooks == (warnings.showwarning, sys.excepthook, tuple(logging.root.handlers))
        if setup in ('application', 'application_empty'):
            assert manager.config is before[0] and manager._policy is before[1]
            if setup == 'application':
                assert tuple(manager._handlers) == before[2]
            else:
                assert not before[2] and not selected[2] and manager._handlers
            assert manager._run_id == 'application-run'
            if setup == 'application':
                assert any(e['code']=='SABUESO-W-ENRICH-001' for e in sink.events)
        if setup != 'unconfigured':
            assert hooks == (warnings.showwarning, sys.excepthook, tuple(logging.root.handlers))
            assert not manager.config.capture_logging and not manager.config.capture_warnings
            assert manager.config.profile == 'qa'
        else:
            assert manager._policy_configured and manager.config.capture_logging
        """,
        setup,
    )


@pytest.mark.parametrize("restricted", [False, True])
@pytest.mark.parametrize("delivery", ["normal", "filtered", "failed"])
def test_real_card_outcomes_survive_scoped_filtered_and_failed_emission(
    tmp_path, restricted, delivery
):
    fresh(
        tmp_path,
        """
        import sys, warnings
        from contextlib import nullcontext
        import smonitor
        from smonitor.handlers.memory import MemoryHandler
        sink = MemoryHandler()
        manager = smonitor.configure(handlers=[sink], level="DEBUG", profile="user",
            capture_warnings=False, capture_logging=False, capture_exceptions=False,
            routes=[], filters=[])
        import sabueso
        from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
        from sabueso.tools.db.chembl import FixtureChEMBLClient
        from sabueso._private.smonitor.warnings import EnrichmentFailedWarning
        fixtures, restricted, delivery = sys.argv[1:]
        def card():
            resolver = EntityResolver(FixtureUniProtClient(fixtures),
                rcsb_client=FixtureRCSBClient(fixtures))
            client = FixtureChEMBLClient(fixtures, failing={"CHEMBL5834"})
            result, _ = sabueso.resolve_protein_card("P52270", resolver, chembl={}, chembl_client=client)
            return result
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            with smonitor.diagnostic_scope() if restricted=='True' else nullcontext():
                baseline = card()
        def outcomes(result):
            return [(e.get('source'),e.get('status'),e.get('detail'))
                    for e in result.quality['enrichments']]
        original = outcomes(baseline)
        assert any(source=='ChEMBL' and status=='error' for source,status,detail in original)
        sink.events.clear()
        if delivery == 'filtered':
            smonitor.configure(level='CRITICAL')
        elif delivery == 'failed':
            def broken(*args, **kwargs):
                raise OSError('synthetic diagnostic failure')
            smonitor.emit = broken
        before = manager.config, manager._policy, tuple(manager._handlers)
        @smonitor.signal(extra_factory=lambda args,kwargs: {'private':'synthetic-private-frame'})
        def invoke():
            scope = smonitor.diagnostic_scope(safe_extra={'receiving':'sabueso-150'}) if restricted=='True' else nullcontext()
            with scope:
                return card()
        policy = smonitor.get_capture_policy()
        with warnings.catch_warnings(record=True) as seen:
            warnings.simplefilter('always')
            result = invoke()
        assert outcomes(result) == original
        assert any(issubclass(w.category,EnrichmentFailedWarning) for w in seen)
        events = [e for e in sink.events if e.get('code')=='SABUESO-W-ENRICH-001']
        if delivery == 'normal':
            assert len(events)==1
            event = events[0]
            if restricted == 'True':
                assert event['context'] is None
                assert event['extra']['receiving']=='sabueso-150'
                assert 'synthetic-private-frame' not in str(event)
                assert 'detail' not in event['extra'] and 'subject' not in event['extra']
            else:
                assert event['extra']['subject'] and event['extra']['detail']
        else:
            assert not events
        assert manager.config is before[0] and manager._policy is before[1]
        assert tuple(manager._handlers)==before[2]
        assert smonitor.get_capture_policy()==policy
        """,
        str(Path(__file__).resolve().parents[2] / "temp_data"),
        str(restricted),
        delivery,
    )
