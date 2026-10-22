import re

from sabueso._private.argdigest._shared import refuse
from sabueso.core.errors import _diagnostic_details_allowed

# Four-character PDB ids, and the extended form RCSB has announced (pdb_ + 8 characters).
PDB_ID = re.compile(r"[0-9][A-Z0-9]{3}|PDB_[0-9]{4}[0-9A-Z]{4}")


def digest_structures(structures, caller=None):
    """``"all"``, one PDB id, or an iterable of PDB ids; ids are returned upper-case.

    A single id is wrapped: iterating the string would otherwise request one "structure"
    per character, each recorded as not found, a plausible wrong result.
    """
    if isinstance(structures, str):
        if structures.strip().lower() == "all":
            return "all"
        structures = [structures]
    try:
        ids = [str(s).strip().upper() for s in structures]
    except TypeError:
        raise refuse(
            "structures",
            structures,
            caller,
            'expected "all", a PDB id or a list of PDB ids',
        ) from None
    wrong = [s for s in ids if not PDB_ID.fullmatch(s)]
    if wrong:
        reason = (
            f"not PDB ids: {wrong}" if _diagnostic_details_allowed() else "not PDB ids"
        )
        raise refuse("structures", structures, caller, reason)
    return ids
