"""Measure one declared public structural task without acquisition or timing tests.

Run with the editable SDK installed, from the repository root. The output directory
must not exist. Timing and tracemalloc observations are separate executions; setup
is excluded from each measured operation. This is a diagnostic, not a speed gate.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import platform
import socket
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 2:
        parser.error("--repeats must be at least two")
    args.output_directory.mkdir(parents=True, exist_ok=False)

    import sabueso
    from sabueso.core.card import Card
    from sabueso.core.snapshot import canonical_json

    def forbidden(*unused_args, **unused_kwargs):
        raise AssertionError("Source access is forbidden in this public measurement")

    socket.create_connection = forbidden
    socket.socket.connect = forbidden
    public = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")
    payload = public.read_bytes()
    card = Card.from_dict(json.loads(payload))
    counter = 0

    def selection():
        return card.explore().access.select(
            "structures",
            fields=["method", "resolution", "coverage"],
            where={"structure_ref": "pdb:1SUX"},
        )

    def save(selected):
        nonlocal counter
        counter += 1
        path = args.output_directory / f"reading-{counter}.json"
        receipt = selected.save(path)
        return path, receipt

    observations = {}

    def measure(name, setup, operation):
        # Warm-up is explicit and excluded. Fresh setup prevents cache reuse
        # across samples, except for the intentionally cached page operation.
        prepared = setup()
        output = operation(prepared)
        del prepared, output
        samples = []
        for _ in range(args.repeats):
            prepared = setup()
            gc.collect()
            start = time.perf_counter_ns()
            output = operation(prepared)
            samples.append((time.perf_counter_ns() - start) / 1e9)
            del prepared, output
        prepared = setup()
        gc.collect()
        tracemalloc.start()
        output = operation(prepared)
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        observations[name] = {
            "seconds": samples,
            "median_seconds": statistics.median(samples),
            "traced_peak_allocated_bytes": peak,
            "traced_retained_allocated_bytes": retained,
        }
        del prepared, output

    measure("capture", lambda: card, lambda c: c.explore())
    measure(
        "materialize_and_select",
        lambda: card.explore(),
        lambda explorer: explorer.access.select(
            "structures",
            fields=["method", "resolution", "coverage"],
            where={"structure_ref": "pdb:1SUX"},
        ),
    )
    measure("cached_page", selection, lambda s: s.page(limit=1, max_bytes=8192))
    measure("save", selection, save)
    measure(
        "read_and_verify",
        lambda: save(selection()),
        lambda saved: sabueso.read_exploration(
            saved[0], expected_digest=saved[1]["bundle_digest"]
        ),
    )
    selected = selection()
    page = selected.page(limit=1, max_bytes=8192)
    assert page["page"]["complete"] and page["page"]["values_complete"]
    assert len(page["items"]) == selected.count == 1
    assert page["items"][0]["cells"]["method"]["value"] == "X-ray"
    saved_path, receipt = save(selected)
    reading = sabueso.read_exploration(
        saved_path, expected_digest=receipt["bundle_digest"]
    )
    assert reading.validation["integrity"] == "verified"
    report = {
        "format": "card_exploration_cost_observation@1",
        "owner": "uibcdf/sabueso#148",
        "source_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "working_tree_diff_sha256": hashlib.sha256(
            subprocess.check_output(
                [
                    "git",
                    "diff",
                    "HEAD",
                    "--",
                    "sabueso",
                    "devtools/measure_card_exploration.py",
                ]
            )
        ).hexdigest(),
        "sdk_version": sabueso.__version__,
        "implementation_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                Path("sabueso/core/card_access.py"),
                Path("sabueso/core/card_structure_page.py"),
                Path("sabueso/core/card_scientific_access.py"),
                Path("sabueso/core/card_exploration_adapter_v1.py"),
                Path("sabueso/core/card_exploration_storage.py"),
                Path("sabueso/core/card_exploration_science.py"),
                Path("sabueso/core/card_structure_selection_v1.py"),
                Path(__file__).relative_to(Path.cwd()),
            )
        },
        "python": sys.version,
        "platform": platform.platform(),
        "input": {"path": str(public), "sha256": hashlib.sha256(payload).hexdigest()},
        "task": {
            "topic": "structures",
            "fields": ["method", "resolution", "coverage"],
            "where": {"structure_ref": "pdb:1SUX"},
            "limit": 1,
            "max_bytes": 8192,
            "underlying_count": 7,
            "selected_count": 1,
        },
        "measurement": {
            "timing_repeats": args.repeats,
            "excluded_warmup_per_operation": 1,
            "memory_repeats": 1,
            "setup": "Excluded; fresh capture/result for each sample. Cached page setup includes original materialization. Card loading and imports excluded.",
            "memory": "New Python allocations traced only during the operation, in a separate execution. Setup allocations excluded; not process RSS or whole-workflow memory.",
            "limits": "Single public input/task, warm filesystem, serial local observations. No tokenizer, remote/source latency, scaling guarantee, timing threshold or researcher acceptance.",
        },
        "observations": observations,
        "sizes": {
            "input_file_bytes": len(payload),
            "captured_card_canonical_bytes": len(
                canonical_json(card.to_dict()).encode()
            ),
            "complete_page_canonical_bytes": len(canonical_json(page).encode()),
            "saved_session_bytes": saved_path.stat().st_size,
        },
        "source_queries": 0,
        "validation": reading.validation,
    }
    (args.output_directory / "receipt.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    # Each exact output path was created by this invocation. Keep only the receipt.
    for index in range(1, counter + 1):
        (args.output_directory / f"reading-{index}.json").unlink()
    print(
        json.dumps({"observations": observations, "sizes": report["sizes"]}, indent=2)
    )


if __name__ == "__main__":
    main()
