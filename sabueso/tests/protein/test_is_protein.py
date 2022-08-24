"""
Unit and regression test for the entity.protein.is_protein method of the library sabueso.
"""

# Import package, test suite, and other packages as needed
import sabueso as sab

def test_is_protein_1():

    is_uniprot = sab.protein.is_protein('P12345')
    assert is_uniprot==True

def test_is_protein_2():

    is_uniprot = sab.protein.is_protein('uniprot_id:P12345')
    assert is_uniprot==True


