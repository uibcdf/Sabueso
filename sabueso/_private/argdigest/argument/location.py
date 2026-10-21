from copy import deepcopy

from sabueso._private.argdigest._shared import refuse


def digest_location(location, caller=None):
    if isinstance(location, dict):
        return deepcopy(location)
    raise refuse(
        "location", location, caller, "expected a typed literal location mapping"
    )
