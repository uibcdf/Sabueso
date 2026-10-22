from sabueso._private.argdigest._shared import refuse


def digest_equals(equals, caller=None):
    if caller == "sabueso.core.card_exploration.filter":
        # The selected result's declared column supplies the type/unit contract.
        return equals
    if isinstance(equals, str):
        return equals
    raise refuse("equals", equals, caller, "label/kind equality requires a string")
