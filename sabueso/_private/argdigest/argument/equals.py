from sabueso._private.argdigest._shared import refuse


def digest_equals(equals, caller=None):
    if isinstance(equals, str):
        return equals
    raise refuse("equals", equals, caller, "label/kind equality requires a string")
