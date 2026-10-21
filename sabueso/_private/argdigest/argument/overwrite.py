from sabueso._private.argdigest._shared import boolean


def digest_overwrite(overwrite, caller=None):
    return boolean("overwrite", overwrite, caller)
