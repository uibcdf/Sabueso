from copy import deepcopy

from sabueso._private.argdigest._shared import refuse


def digest_where(where, caller=None):
    if where is None or isinstance(where, dict):
        return deepcopy(where)
    raise refuse("where", where, caller, "expected a mapping of column equalities")
