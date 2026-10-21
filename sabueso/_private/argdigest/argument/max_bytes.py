from sabueso._private.argdigest._shared import refuse


def digest_max_bytes(max_bytes, caller=None):
    if type(max_bytes) is int and 1024 <= max_bytes <= 1048576:
        return max_bytes
    raise refuse(
        "max_bytes", max_bytes, caller, "expected an integer from 1024 to 1048576"
    )
