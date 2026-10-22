from sabueso._private.argdigest._shared import optional_text


def digest_locator(locator, caller=None):
    """Where in the publication: a figure, table, page or section."""
    if caller in {
        "sabueso.core.card_access.catalog",
        "sabueso.core.card_exploration.inspect",
    }:
        if locator is None:
            return None
        from .location import digest_location

        return digest_location(locator, caller)
    return optional_text("locator", locator, caller)
