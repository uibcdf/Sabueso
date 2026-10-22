from sabueso._private.argdigest._shared import refuse


def digest_column(column, caller=None):
    if caller in {
        "sabueso.core.card_exploration.filter",
        "sabueso.core.card_exploration.sort",
    }:
        if isinstance(column, str) and column.strip():
            return column
        raise refuse("column", column, caller, "expected a declared column key")
    if isinstance(column, str) and column in ("label", "kind"):
        return column
    raise refuse("column", column, caller, "available columns: label, kind")
