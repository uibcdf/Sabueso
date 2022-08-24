"""
Unit and regression test for the tools.string.pdb_id.string_is_pdb_id method of the library sabueso.
"""

# Import package, test suite, and other packages as needed
import sabueso as sab

def test_is_accessible():

    assert sab.database.UniProtKB.is_accessible()

