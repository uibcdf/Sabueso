from sabueso._private.argdigest._shared import refuse


def digest_kind(kind, caller=None):
    if isinstance(kind, str) and kind in ("topics", "fields", "selections"):
        return kind
    raise refuse("kind", kind, caller, "expected topics, fields or selections")
