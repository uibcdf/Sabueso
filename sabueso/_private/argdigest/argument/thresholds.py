def digest_thresholds(thresholds, caller=None):
    """None (the defaults), or {name: quantity} for active_max, weak_max and
    single_point_min. Bare numbers are refused: their unit would be a guess (#32)."""
    from sabueso.core.bioactivities import resolve_thresholds
    from sabueso.core.errors import ArgumentError, _diagnostic_details_allowed

    if thresholds is None:
        return None
    if not isinstance(thresholds, dict):
        raise ArgumentError(
            argument="thresholds",
            value=thresholds,
            caller=caller,
            reason="expected a dict of quantities, or None",
        )
    try:
        resolve_thresholds(thresholds)
    except ArgumentError as error:
        if not _diagnostic_details_allowed():
            raise ArgumentError(
                argument="thresholds", reason="invalid thresholds"
            ) from None
        raise ArgumentError(
            str(error).replace(
                "Argument 'thresholds'", f"Argument 'thresholds' of {caller}", 1
            )
        ) from None
    return thresholds
