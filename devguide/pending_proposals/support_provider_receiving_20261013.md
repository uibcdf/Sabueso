# Receiving DepDigest 0.15.1 and SMonitor 0.20.0 (#112, #31, #46)

The existing Python 3.14 development environment now uses editable local
checkouts corresponding to published
[DepDigest 0.15.1](https://github.com/uibcdf/depdigest/releases/tag/0.15.1) and
[SMonitor 0.20.0](https://github.com/uibcdf/smonitor/releases/tag/0.20.0).
The [receiving receipt](support_provider_receiving_20261013.json) records actual
source hashes, versions, checks and limits. Implementation and runtime dependency
declarations are byte-equivalent to their release tags; later checkout changes
are documentation only.

DepDigest is `0.15.1+2.gd5c5121` at `d5c5121`; SMonitor is
`0.20.0+1.gb38c06b` at `b38c06b`. Their import paths and installed metadata agree
outside the checkout, together with Sabueso, ArgDigest, Ackredit, PyUnitWizard
and Recorda. Both provider checkouts were clean fast-forward updates; their
implementation was not changed locally and no separate test environment was made.

On Sabueso `760a177` (executable code equivalent to qualified `792bd0d`),
112 diagnostic/argument/table/attribution/dependency cases pass, including
missing-pandas install hints, dimensional table values, catalog profiles,
structured events and caller warning locations. The full local-original offline
suite passes 6,266 cases in 127.59 seconds with thirteen expected fixture warnings.
The MOLI receiver passes all 19 public cases against this environment. Tests use
twelve pytest-receptor workers and fatal SQLite/unraisable guards. Dependency
release preflight passes. Test timings are records, not performance comparisons.

Sabueso continues to use DepDigest's `@dep_digest` optional-pandas guard and its
existing SMonitor bundle/bootstrap. Runtime floors remain `depdigest>=0.11.0`
and `smonitor>=0.17.0`, already allowing these releases; packaging and installed
qualification pins remain unchanged. The stale diagnostic-guide environment
floor is corrected to its actual `>=0.17.0` declaration.

DepDigest's new overlapping `DeclaredRegistry` requests and selective adapter
inspection are opt-in capabilities unused by Sabueso. SMonitor's new
`bootstrap_policy=False` declaration-only emission is also unused; its default
`True` retains the earlier first-use behavior. Adopting either capability later
requires its documented floor and receiving contract, rather than inferring
adoption from a newer installed version.

This receipt qualifies the existing Linux/Python 3.14 editable consumer scope.
It does not establish a new combined public-Conda installed pair, a new hosted
OS/minor matrix, or a Sabueso release. Those scopes retain their own gates in the
[release proposal](release_consolidation_0150.md). Original source/release/consumer
receipts, frozen cards, scientific payloads and publication snapshots stay unchanged.
No online provider query or private pilot material enters this checkpoint.
