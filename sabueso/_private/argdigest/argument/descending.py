from sabueso._private.argdigest._shared import boolean


def digest_descending(descending, caller=None):
    return boolean("descending", descending, caller)
