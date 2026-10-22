from copy import deepcopy

from sabueso._private.argdigest._shared import refuse


def digest_order_by(order_by, caller=None):
    if order_by is None or isinstance(order_by, dict):
        return deepcopy(order_by)
    raise refuse(
        "order_by", order_by, caller, "expected column, descending and optional unit"
    )
