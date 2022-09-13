"""
Unit and regression test for the tools.string.pdb_id.string_is_pdb_id method of the library sabueso.
"""

# Import package, test suite, and other packages as needed
import sabueso as sab


def test_is_string_pdb_id_1():

    is_pdb_id = sab.database.RCSB_PDB.pdb_id.is_pdb_id('1BRS')
    assert is_pdb_id==True

def test_is_string_pdb_id_2():

    is_pdb_id = sab.database.RCSB_PDB.pdb_id.is_pdb_id('X3BD')
    assert is_pdb_id==False

def test_is_string_pdb_id_3():

    is_pdb_id = sab.database.RCSB_PDB.pdb_id.is_pdb_id('P00648')
    assert is_pdb_id==False

