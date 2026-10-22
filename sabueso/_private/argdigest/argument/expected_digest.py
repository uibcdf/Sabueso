from sabueso._private.argdigest._shared import refuse
from sabueso.core.snapshot import SNAPSHOT_ID


def digest_expected_digest(expected_digest, caller=None):
    if expected_digest is None or (
        isinstance(expected_digest, str) and SNAPSHOT_ID.fullmatch(expected_digest)
    ):
        return expected_digest
    raise refuse(
        "expected_digest", expected_digest, caller, "expected sha256:<64 hex> or None"
    )
