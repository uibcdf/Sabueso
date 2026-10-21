from sabueso._private.argdigest._shared import refuse


def digest_cursor(cursor, caller=None):
    if cursor is None or isinstance(cursor, str) and cursor:
        return cursor
    raise refuse("cursor", cursor, caller, "expected a nonempty opaque cursor or None")
