<!--
CANONICAL MOLI GUIDE — component copies should remain synchronized.
Canonical source: https://github.com/uibcdf/moli/blob/main/MOLI_GUIDE.md
Platform architecture: https://github.com/uibcdf/moli/tree/main/architecture_1.0
-->

# MOLI component guide

This guide defines the shared governance rules for components of the MOLI platform.

## Where governance lives

Use `uibcdf/moli` for contracts, terminology, policies, and decisions that affect two or more MOLI components or the platform as a whole.

A component repository remains authoritative for its own implementation, tests, local API, scientific evidence, releases, and component-specific development decisions.

MOLI Platform Architecture 1.0 defines what the platform concepts mean. The MOLI development guide defines how repositories coordinate. Governance documents must not silently redefine frozen architecture.

## MOLI components

The authoritative registry is `moli.toml`. Initial MOLI components are:

- Sabueso — Knowledge context;
- Praxis — Methodological / Know-how context;
- Nextia — Discovery context;
- MolSysSuite — molecular modeling ecosystem;
- MOLI Agent — optional scientific reasoning and agency.

Scientific Context is a conceptual grouping of Sabueso, Praxis, and Nextia; it is not a separate component repository.

MolSysSuite is a MOLI component **with delegated internal governance**. MOLI governs MolSysSuite at the platform boundary. `uibcdf/molsyssuite` is the normative owner of its members' engineering and modeling policies, contracts, adoption, releases, and enforcement. MOLI engineering rules for direct components do not automatically become member rules; MolSysSuite remains responsible for platform contracts it owes to MOLI.

## Ownership rule

> **A concern is governed at the lowest level that owns the shared contract it affects.**

Examples:

- a Sabueso-only implementation bug → `uibcdf/sabueso`;
- a Nextia-only DiscoveryEngine bug → `uibcdf/nextia`;
- a Sabueso ↔ Nextia SourceAssertion/Evidence contract → `uibcdf/moli`;
- a Praxis ↔ Nextia Capability/Protocol invocation contract → `uibcdf/moli`;
- a TopoMT-only bug → `uibcdf/topomt`;
- a TopoMT ↔ MolSysMT shared contract → `uibcdf/molsyssuite`;
- a MolSysSuite ↔ Nextia platform contract → `uibcdf/moli`.

## Reporting bugs and proposals

Everyone who uses, develops, maintains or operates a MOLI component or UIBCDF support tool must communicate actionable bugs, missing capabilities, improvement opportunities and new feature proposals through the owning GitHub issue. Open a new issue or add concrete evidence to an existing one. This applies equally to Sabueso, MolSysSuite members, pytest-receptor, gh-run-receptor, the Conda build/upload and Sphinx-to-Pages actions, and future repositories. If you cannot open an issue, ask the responsible maintainer to record it. Do not leave the finding only in a chat, local workaround or downstream repository. Reporting does not promise immediate implementation. Follow [MOLI's issue-feedback rule](https://github.com/uibcdf/moli/blob/main/devguide/governance/reporting_protocol.md#universal-issue-feedback-commitment); use private security reporting for exploitable or confidential findings.

Report a one-repository concern in the repository that owns it.

Report a shared MOLI-component/platform contract concern in `uibcdf/moli`. Cross-link component-local implementation issues where needed.

For concerns internal to MolSysSuite, follow MolSysSuite governance rather than duplicating them in MOLI.

GitHub issues are the stable identity for bugs/proposals. Durable analysis or decisions may be recorded under the owning repository's `devguide/`; small findings need no extra report.

## Durable instructions for development agents

An incident does not by itself call for an `AGENTS.md` change. Report a bug or need to its owner; put source behavior, scientific facts, API details and edge cases in the fix, regression tests and relevant technical documentation as applicable. Use `AGENTS.md` only for an accepted, lasting instruction about **how contributors or agents should work** across future tasks in that file's scope, when existing guidance is insufficient. Put a repository-wide working instruction in the root file and a directory-specific one in the nested file. Do this with the fix or decision; open a linked adoption issue only when that accepted instruction cannot be placed in the same change. Routine defect triage does not require asking a human whether to edit `AGENTS.md`; the issue-feedback and human-review rules still apply. Point to the authoritative policy rather than copying long procedures.

Repositories with a `devguide/` keep `devguide/AGENTS.md` for instructions specific to that directory: maintained guidance, active issue-backed queues, and historical archives. Propose a locally accepted **agent working instruction** to the lowest owner only when evidence supports use across repositories: MOLI for direct components or a cross-suite boundary, MolSysSuite for its members. Route an ordinary technical defect to its provider issue. Adoption by another repository requires its own decision. Follow [MOLI's agent-instruction lifecycle](https://github.com/uibcdf/moli/blob/main/devguide/governance/agent_instruction_lifecycle.md); MolSysSuite governs rollout within its members.

## Cross-component feedback

When work in one component exposes a missing or limiting capability in another:

1. report the need to the provider repository or its delegated governance domain;
2. include the consuming use case and why it matters;
3. cross-link local workaround or blocked work;
4. escalate to `uibcdf/moli` when the issue changes a contract between MOLI components or requires platform policy.

For a change needed in another repository, open or update the provider issue
when no fix is ready; submit a concrete fix as a pull request for owner review
and link its issue. If the work is urgent and Diego or Liliana are doing or
directly supervising it, ask them whether the change should be an issue, pull
request or direct commit and push. Direct push requires their explicit
permission for that change. The provider's own team keeps its local review
practice. Follow the [cross-repository contribution route](https://github.com/uibcdf/moli/blob/main/devguide/governance/cross_component_feedback.md#contributing-a-fix-across-repositories).

When changing a shared auxiliary library or UIBCDF development action, also
notify the governance domain of any plausible effect on other packages through
an issue: `uibcdf/moli` for direct components or a platform contract,
`uibcdf/molsyssuite` for suite members, and both when each has distinct work.
Link the provider issue, affected consumers, compatibility and release impact,
and owner-local follow-ups. Give notice before publishing the provider change
or starting consumer rollout when the impact is known in advance; report later
discoveries promptly.
An existing issue can carry the notice. Follow the
[cross-component feedback rule](https://github.com/uibcdf/moli/blob/main/devguide/governance/cross_component_feedback.md#changes-to-shared-auxiliary-providers).

## UIBCDF development infrastructure supporting MOLI

UIBCDF maintains four shared resources used by MOLI development. They are [registered separately from scientific components](https://github.com/uibcdf/moli/blob/main/devguide/governance/support_infrastructure.md). Use each where its boundary applies:

| Resource | Use | Report a defect or improvement |
| --- | --- | --- |
| [Pytest Receptor](https://github.com/uibcdf/pytest-receptor) | Python test output for agents and CI | [Provider issues](https://github.com/uibcdf/pytest-receptor/issues) |
| [GH Run Receptor](https://github.com/uibcdf/gh-run-receptor) | Inspect Actions run evidence | [Provider issues](https://github.com/uibcdf/gh-run-receptor/issues) |
| [Conda build/upload action](https://github.com/uibcdf/action-build-and-upload-conda-packages) | Build and publish Conda packages | [Provider issues](https://github.com/uibcdf/action-build-and-upload-conda-packages/issues) |
| [Sphinx-to-Pages action](https://github.com/uibcdf/action-sphinx-docs-to-gh-pages) | Publish Sphinx docs to GitHub Pages | [Provider issues](https://github.com/uibcdf/action-sphinx-docs-to-gh-pages/issues) |

The provider owns its tool. MOLI owns usage policy for directly governed components and platform-facing obligations; MolSysSuite owns the rules for use by its members. The receptors also remain MolSysSuite auxiliary members. Link provider issues from any blocked consumer work. A repository without the relevant test, release or documentation route need not add that tool.

## MOLI engineering baseline

MOLI owns the engineering baseline for directly governed components. Applicable policies are registered in `moli.toml` and documented under `uibcdf/moli/devguide/policies/`. MolSysSuite owns its member baseline in `suite.toml` and its own `devguide/`. Similar values in both registries are separate governance decisions.

For directly governed repositories carrying the `python-package` capability, the baseline includes Python support, CI coverage, Ruff/pytest quality tooling, applicable UIBCDF support libraries, developer receptors, distribution, release-version semantics, repository badge evidence, and archival/DOI rules when applicable. MolSysSuite sets corresponding requirements for its members.

Routine local development and push/PR tests for directly governed Python packages use Python 3.14, including local pytest runs. Keep the full required test matrix for every supported minor, currently 3.11–3.14. MolSysSuite sets its member rule independently in its own registry and guide. Its [development environment recipe](https://github.com/uibcdf/molsyssuite/blob/main/devtools/conda-envs/README.md) names `molsyssuite@uibcdf_3.14`; MolSysSuite governs which members are qualified for it and how to create it.

During authorized direct-push development, group small local commits when a remote checkpoint is unnecessary. Match checks to the change: documentation and research evidence need applicable local checks; changed scientific or public behavior needs targeted regressions and broader checks where affected. Consider `[skip ci]` only for a locally checked push that the repository permits, with a reliable route to recover deferred code tests. Normally finish code work with an unskipped push and inspect its applicable gates on the actual head; an explicitly authorized manual run of those same exact-head gates is also valid. A skipped run is not passing evidence and cannot evade required PR checks. For admission, release or publication, every mandatory gate must actually pass for the exact candidate and required installed artifact/closure. A marker on the original producer commit does not disqualify it when the authorized manual route proves those gates against the original commit, file and digest; never rebuild the recorded file just to change its CI status. Follow [MOLI's direct-push CI decision rule](https://github.com/uibcdf/moli/blob/main/devguide/policies/python_ci_policy.md#validation-during-direct-push-development) and [candidate evidence lifecycle](https://github.com/uibcdf/moli/blob/main/devguide/policies/release_version_policy.md#candidate-evidence-lifecycle); MolSysSuite owns its member rule and recovery implementation.

Linux and macOS are the operating-system support baseline for public Python packages. Linux has a routine gating lane; macOS needs recurring tests and installed-package evidence before release. Windows is optional and is claimed only after equivalent evidence. Record current claims in the component README and in `moli.toml` for direct components; MolSysSuite records member claims internally. Follow [MOLI's Python CI policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/python_ci_policy.md) for cadence, release checks and bounded macOS exceptions.

macOS support is currently limited to Apple Silicon (arm64). Intel-based macOS (x86_64) is not part of the supported platform matrix. Support may be reconsidered if there is demonstrated user demand. A component claims arm64 only after its own installed-package and runtime evidence; noarch packaging or a solver result alone is insufficient. MolSysSuite governs the architecture rollout for its members.

Review public API contracts for ArgDigest, optional or heavy dependencies for DepDigest, user-facing diagnostics for SMonitor, and physical quantities for PyUnitWizard. Use each library where its boundary exists; record justified non-applicability or a bounded exception in the component's review issue. Follow [MOLI's support-library policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/python_support_libraries_policy.md) for the exact applicability rule.

## Physical quantities and units

Treat a wrong unit as a scientific correctness failure. A quantity must keep its value, unit and meaning through calculation, storage and communication. Serialized values carry their negotiated unit inside the same object; readers verify the record and explicitly state the expected field and unit or dimension. Never guess from a bare number, field name or session default. Name boundary conversion units explicitly, and test under a non-default unit policy. A consistent but wrongly labelled source also needs domain or cross-source checks. Follow [MOLI's quantity integrity policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/quantity_integrity_policy.md).

PyUnitWizard owns the serialization design and codec. Follow its [canonical guide](https://github.com/uibcdf/pyunitwizard/blob/main/standards/PYUNITWIZARD_GUIDE.md#storing-and-exchanging-quantities-provisional), and read the [design record](https://github.com/uibcdf/pyunitwizard/issues/83) and [QuantityRecord implementation](https://github.com/uibcdf/pyunitwizard/issues/82) before designing a persisted representation; Sabueso is the first consumer. Components track their own schema migration and applicable format support. MOLI tracks the shared [quantity contract](https://github.com/uibcdf/moli/issues/12), while MolSysSuite tracks its member adoption.

When an agent runs Python tests, use the published pytest-receptor with `--receptor=llm`; use `--receptor=ci` in pytest CI logs. Use a published gh-run-receptor as the preferred first inspection of Actions runs, with GitHub conclusions authoritative and native `gh run view` as fallback. Follow [MOLI's developer-tools policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/python_developer_tools_policy.md) for versions, safeguards, and exceptions. These developer tools are not runtime dependencies.

The official user-installation route for a public Python component is the `uibcdf` Conda channel with third-party packages from `conda-forge`. A public PyPI route is optional, needs a documented reason, and may be claimed only after its published package and complete dependency closure pass clean-install verification; pytest-receptor uses PyPI for pytest plugin discovery. Install a local checkout for development with `python -m pip install --no-deps --editable .` after provisioning its Conda environment; this is not publication. For co-development, install each participating installable Python component from its own checkout in the compatible shared Conda environment, verify import paths, and track components that cannot yet join. Non-Python scaffolds do not require pip installation. MolSysSuite owns qualification and rollout for its members, including the named 3.14 environment. Keep development and test environments in `devtools/conda-envs/`, align required runtime dependencies between `pyproject.toml` and the Conda recipe, and build public Conda packages through the shared UIBCDF action. Required CI must acquire Conda-only third-party dependencies through a resolvable Conda environment; a tracked, full-commit source route may cover a sibling version unavailable on the configured channels for tests. Follow [MOLI's distribution policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/python_distribution_policy.md) for recipe, CI and release evidence. Do not advertise an unpublished package or channel.

Before creating or editing a public component GitHub Release, check that its visible title (`name`) is exactly the canonical `X.Y.Z` version, identical to the release tag (`tag_name`) and project/package version. Use `gh release create X.Y.Z --title X.Y.Z` or set `name` and `tag_name` identically through the API. Put project names and descriptive text in the release notes. Policy-release namespaces and archive tags keep their separate rules; historical titles are not changed by this instruction. Follow [MOLI's release-version policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/release_version_policy.md#github-release-title). MolSysSuite owns delivery of the equivalent member rule.

For a public release with Zenodo archival intent, maintain a README **Current release status** stating the exact version, archive evidence state, verified DOI links when they resolve, and the artifacts actually archived. `CITATION.cff` is the preferred metadata source; use `.zenodo.json` only when Zenodo-specific fields require it, because it takes precedence during ingestion. A release, integration delivery or registered DOI alone does not prove archival. Check the public record and both DOI destinations before claiming a verified archive or displaying a DOI badge. Order conditional badges as tests, coverage, deployed docs, release, DOI and verified distribution. Follow [MOLI's Zenodo policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/zenodo_policy.md) and [badge policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/repository_badges.md).

When meaningful coverage is measured, display a dynamic Codecov percentage for the repository in its main README only after an accepted, recent default-branch report. State the test scope and cadence; a scheduled report may lag newer commits. A missing, stalled or `unknown` report calls for an owner-local producer fix, not a static percentage. Incubating repositories without meaningful executable code record why the badge is inapplicable and when to reassess. Follow the [badge policy](https://github.com/uibcdf/moli/blob/main/devguide/policies/repository_badges.md#coverage-percentage); MolSysSuite owns member adoption.

## Starting a new MOLI component repository

Register a new directly governed component in `moli.toml` before treating its repository as admitted. Start it with a root `AGENTS.md` that points to the vendored `MOLI_GUIDE.md` and states the issue-feedback and durable agent-working-instruction actions, a `devguide/AGENTS.md` that distinguishes current guidance and active issue queues from archive/history, the reporting queues/template, and the governance check. Use [MOLI's onboarding guide](https://github.com/uibcdf/moli/blob/main/devguide/governance/new_component_onboarding.md) and [agent-instruction starter](https://github.com/uibcdf/moli/blob/main/devguide/templates/component_agent_instructions.md). Run `python devtools/scripts/check_repository.py <checkout> --canonical-guide MOLI_GUIDE.md` from MOLI before calling the governance surface complete; a new repository must not depend on a later migration to acquire these instructions.

When registering a new direct Python component, also declare its `python-package` capability, `python_ecosystem_review` and `python_distribution_review` issues, `supported_os`, and an owner-local `os_support_review` issue and state in `moli.toml`. An incubating component may have no supported-OS claim while the review is pending. The issues record applicability, adoption evidence, and exceptions. MOLI's registry validation and scheduled component audit guard this onboarding step. MolSysSuite owns its separate starter kit and member admission.

A component may add stricter local requirements. It must not silently contradict an applicable MOLI engineering policy; deviations require a tracked exception with rationale and an exit condition.

MolSysSuite adopts and versions its own member engineering baseline. It may align with a MOLI rule, but a MOLI policy change does not silently change the member rule. Platform scientific and interoperability contracts still bind MolSysSuite as a MOLI component.

## Architectural boundaries

Respect the frozen MOLI distinctions, including:

- Knowledge ≠ Know-how ≠ Discovery;
- SourceAssertion ≠ Evidence ≠ Provenance;
- Capability ≠ Protocol;
- DiscoveryProject ≠ DiscoveryEngine;
- Strategy ≠ Protocol; Campaign ≠ Protocol;
- Artifact ≠ Result ≠ Observation ≠ Evidence;
- semantic ownership ≠ visibility ≠ publication status;
- promotion ≠ publication.

If implementation pressure suggests changing one of these boundaries, open a platform proposal in `uibcdf/moli`.

## Visibility and confidentiality

A public repository may operate on private scientific content. Do not infer publication rights from semantic ownership or open-source code.

Cross-repository reports must not disclose confidential DiscoveryProjects, proprietary Protocols, molecular Candidates, unpublished Evidence, credentials, or restricted data.

## MolSysSuite internal governance

MolSysSuite's status as a MOLI component does not transfer governance of MolSysMT, TopoMT, MolSysViewer, DockingMT, or other MolSysSuite members to MOLI.

```text
MOLI
  └── MolSysSuite        governed by MOLI at platform boundary
        ├── MolSysMT
        ├── TopoMT
        └── ...           governed internally by MolSysSuite
```

Do not use MOLI governance to duplicate MolSysSuite's member policies, rollout, enforcement, membership, modeling-domain contracts, or repository-local implementation policy. MolSysSuite owns the member engineering baseline; MOLI owns its own direct-component baseline and the platform obligations of MolSysSuite as a unit.

## Before finishing cross-component work

Ask:

1. Is the implementation change in the repository that owns it?
2. Did this expose a provider limitation that should be reported at its owning level?
3. Did it change a contract between MOLI components requiring a platform issue?
4. Does it preserve architecture, provenance, visibility, and authority boundaries?
5. Is any temporary workaround cross-linked to its owning issue?

Detailed policies belong in the canonical `uibcdf/moli/devguide/`.
