from sabueso._private.argdigest._shared import refuse


def digest_column(column, caller=None):
    if isinstance(column, str) and column in ("label", "kind"):
        return column
    raise refuse("column", column, caller, "available columns: label, kind")
