from sabueso._private.argdigest._shared import optional_text


def digest_locator(locator, caller=None):
    """Where in the publication: a figure, table, page or section."""
    if caller == "sabueso.core.card_access.catalog":
        if locator is None:
            return None
        from .location import digest_location

        return digest_location(locator, caller)
    return optional_text("locator", locator, caller)
