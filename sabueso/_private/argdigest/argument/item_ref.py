import re

from sabueso._private.argdigest._shared import refuse


def digest_item_ref(item_ref, caller=None):
    if isinstance(item_ref, str) and re.fullmatch(r"XI_[0-9a-f]{64}", item_ref):
        return item_ref
    raise refuse("item_ref", item_ref, caller, "expected an XI_ item reference")
