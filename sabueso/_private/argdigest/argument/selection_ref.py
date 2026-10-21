import re

from sabueso._private.argdigest._shared import refuse


def digest_selection_ref(selection_ref, caller=None):
    if isinstance(selection_ref, str) and re.fullmatch(
        r"XA_[0-9a-f]{64}", selection_ref
    ):
        return selection_ref
    raise refuse(
        "selection_ref", selection_ref, caller, "expected an XA_ selection reference"
    )
