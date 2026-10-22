from sabueso._private.argdigest._shared import path_list


def digest_fields(fields, caller=None):
    """One field path, or an iterable of field paths; returned as a list."""
    if fields is None and caller == "sabueso.core.card_access.select":
        return None
    return path_list("fields", fields, caller)
