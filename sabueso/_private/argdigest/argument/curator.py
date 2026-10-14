from sabueso._private.argdigest._shared import refuse


def digest_curator(curator, caller=None):
    """A curator's declared name; shape validation does not establish human review."""
    if isinstance(curator, str) and curator.strip():
        return curator.strip()
    raise refuse("curator", curator, caller, "expected a non-empty name")
