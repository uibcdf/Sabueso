# Reviewed recovery fixture delivery

The [file inventory](fixture_delivery.json) records the exact 86 recovery inputs,
the derived 0.14.0 schema compatibility card (#134), and the CC BY 4.0
open-article XML for located source review (#92), with their source, digest,
size, recorded terms and delivery decision (#112/#95).
Existing committed fixtures retain their source-specific notice. This inventory
records file decisions; the [source registry](registry.yaml) remains authoritative
for source adoption and terms. No access route or software/article licence grants
unrecorded data rights.

There are **51 repository-delivery inputs** under the recorded declarations and
file-specific obligations in [the fixture notice](../../temp_data/NOTICE.md), and
**37 local-only originals** in protected directories. Unknown, conditional or
explicitly unshared scopes remain local. The original DisProt response also
remains local until its embedded article-quotation rights are qualified. PRIDE's
selected project CC0 and OmniPath's selected CC BY inputs are file-specific
decisions, not source-wide grants.

## Public repository and CI

```bash
python tools/fixture_delivery.py --check
python -m pytest -n 12 -m "not online" --receptor=llm
```

The gate checks input identities, source-term changes and the Git index. A forced
addition of local-only files fails; an unreviewed new fixture also fails.
Git delivery preserves raw `temp_data` bytes through `.gitattributes`, including
checkout with Windows line-ending conversion enabled. Fixture hashes identify
original responses; newline conversion would change those inputs.
Native trailing whitespace is also original response content, so Git whitespace
checks exclude those wire files. The maintained notice and code/docs retain normal
whitespace checks. Original-byte digests remain the integrity gate for responses.
Public tests exclude 25 whole modules that need local originals before module import.
Mixed native-snapshot tests retain public AlphaFill/GlyGen qualification and all
five clients' synthetic malformed/binding checks; nine native SIFTS/LIGYSIS cases
are explicitly skipped unless local input qualification is requested. One native
DisProt sequence-axis case is also explicitly local; synthetic track cases remain public.

CI checks this publication scope before its offline suite. Its passing result is
public-input validation, not native qualification of excluded scopes. Wheels and
sdists omit `temp_data`; public Git delivery has its own data boundary.

## Full local native qualification

Use the existing editable `molsyssuite@uibcdf_3.14` environment:

```bash
python tools/fixture_delivery.py --check --local-inputs
python -m pytest -n 12 -m "not online" --receptor=llm --local-source-inputs
```

The explicit option verifies every required local original's digest before
collection, includes the 25 native modules and runs the ten mixed native cases.
Missing or changed originals fail with their paths; they never become successful
empty-source responses. No download, login, redistribution or live-health claim
is supplied by this option. The local marker is `local_source_inputs`.

Qualify the public suite without local originals when changing this separation.
Keep them intact and restore them after the reversible absence check. Record the
scope and result of each suite separately; historical 5,554-case receipts precede
this explicit split.

## Reopening a local delivery decision

Obtain an applicable file-specific declaration and review it in the owning issue.
Update the inventory, the source registry/notice when needed, ignore protection
and the dependent tests together. Changed source terms invalidate an old file
decision rather than promoting it automatically. Continue scientific development
with already qualified inputs while these decisions remain deferred.
