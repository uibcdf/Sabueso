from sabueso._private.argdigest._shared import refuse

from .item_ref import digest_item_ref


def digest_item_refs(item_refs, caller=None):
    if item_refs is None:
        return None
    if not isinstance(item_refs, (list, tuple)):
        raise refuse(
            "item_refs", item_refs, caller, "expected a sequence of XI_ references"
        )
    refs = [digest_item_ref(ref, caller) for ref in item_refs]
    if len(set(refs)) != len(refs):
        raise refuse("item_refs", item_refs, caller, "duplicate item references")
    return refs
