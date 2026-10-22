from sabueso._private.argdigest._shared import optional_text


def digest_unit(unit, caller=None):
    return optional_text("unit", unit, caller)
