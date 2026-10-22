# Application-owned diagnostics — receiving decision (#150)

Owner: [Sabueso #150](https://github.com/uibcdf/sabueso/issues/150).
Coordination: [MolI #62](https://github.com/uibcdf/moli/issues/62).
Date: 2026-10-22.

## Retained import and emission behavior

Keep the standalone convenience from #31: importing Sabueso selects its existing
SMonitor bootstrap route. Its recommendations enable warning/logging capture;
the effective unconfigured baseline also depends on earlier provider imports.
The original receiving cohort selects ArgDigest's logging-on/warning-capture-off
baseline; the recent cohort selects Sabueso's logging/warning-capture-on baseline.
Configure SMonitor **before importing
Sabueso** when the application owns its settings. Receiving on the selected
modern public providers verifies application/project precedence, reload, first
use, repeated registration and actual catalog emission without policy replacement.
The older declared package floors are not a guarantee of this newer
application-ownership behavior; this receiving qualifies the named cohorts.

The bundle keeps its compatibility bootstrap. This review does not select
`bootstrap_policy=False`; changing the bundle alone would not remove bootstrap
from Sabueso's imports and other providers. An empty handler list is not a
handlerless-emission guarantee. Retain detailed diagnostics outside a caller's
restrictive scope, including existing catalog codes, Python warning behavior,
caller locations and default error text.

Pure registration-only import/emission is **deferred** until a named embedding
host needs no implicit configuration or capture. Review import order, ArgDigest
initialization and actual bundle emission together for that use case. No
runtime dependency-floor upgrade is selected by this review.

## Bounded scoped receiving and reproduced fix

A caller can enter SMonitor's public `diagnostic_scope()` before invoking a
provider-backed API. The selected receiving cohorts provide SMonitor 0.19 /
ArgDigest 0.15 and SMonitor 0.21 / ArgDigest 0.16. The package's older declared
floors do not imply these newer capabilities; an application selecting scoped
collection must provision capable providers. Capability absence retains the
existing detailed compatibility branch; it is not restrictive qualification.

The reproduction found Sabueso-owned diagnostic formatting before SMonitor:
`ArgumentError` evaluated a rejected value's `repr`; shared option/field-path
errors also rendered rejected content; knowledge-query/threshold translation
stringified native errors. Seven tests fail on the original source because
hostile diagnostic methods replace the intended `ArgumentError`.

The fix consults SMonitor's capture permissions **before** constructing these
payloads. With argument or exception-text capture prohibited, use fixed error
prose, omit rejected values from diagnostic reasons, and avoid native error
stringification in those translations. The unknown-threshold error likewise
avoids formatting its rejected key. Detailed-mode wording stays unchanged.
No second capture policy or blanket decorator rewrite is introduced.

This adopts caller-owned restriction at the reviewed argument boundaries and
qualifies real fixture-backed protein resolution with source-failure advice.
Scoped events exclude enclosing frames, ordinary extras and scientific details;
explicit caller-approved primitive facts remain. Filtering or failed catalog
emission preserves the returned Card's recorded source status/detail and the
ordinary Python warning. Providers retain native failure/validation contracts.

A capture scope is **not** redaction of the Card, acquisition records or previously
constructed messages/warnings. Scientific normalization, input iteration and
retained source-error descriptions keep their existing semantics; they are not
SMonitor-owned automatic capture. This is bounded receiving of the named error
paths and real emission, not a secrecy guarantee for arbitrary Sabueso/user code.
Python warning filters and their exception behavior remain Python's contract.

`quality.enrichments[].detail` is a rendered exception description, not a stable
error identity. A catalog exception constructed under restrictive capture can
yield a fixed description there instead of detailed text. Source/status and
scientific result facts remain; no byte-identical cross-policy description is
claimed. Filtering/failure checks compare details under the same capture policy.

## Other optional features

Safe audience-specific maps and nonemitting identity export are **not applicable
to this slice**. Existing catalog resolution/fallback suffices for these events;
no new export or audience API is needed. Revisit for a concrete safe explanation
or export use case. A general diagnostic/operation bridge, shared routing or
retention protocol requires its own consumer and platform review.

The [receiving receipt](evidence/diagnostic_receiving_150_20261022.json) fixes source,
public-provider archives, installed origins, reproduction and executed scope.
The full checkpoint uses public repository inputs, not the separately governed
unshared native originals. Exact-head CI and native gate evidence are recorded
in #150. This is neither a Sabueso release nor consumer scientific acceptance.

The checkpoint also exposed unclosed `HTTPError` resource warnings. The separate
[Sabueso #151](https://github.com/uibcdf/sabueso/issues/151) now identifies and fixes
transport/archive/client ownership; its [lifetime contract](SOURCE_ACCESS.md#http-response-lifetime-151)
and receipt retain the executed scope. No warnings are suppressed. This later
resource fix does not change #150's scoped-capture receiving claims.
