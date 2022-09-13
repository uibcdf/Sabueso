# We start with mmtf-python and some APIs from DBs
import urllib as _urllib
import json as _json

#MMTF
#https://github.com/rcsb/mmtf/blob/master/spec.md#secstructlist
_sec_struct_codes = {0 : "I", #pi helix
                     1 : "S", # bend
                     2 : "H", # alpha helix
                     3 : "E", # extended
                     4 : "G", # 3-10 helix
                     5 : "B", # bridge
                     6 : "T", # turn
                     7 : "C", # coil
                     -1: "X"} # undefined

_dssp_to_abc = {"I" : "c", # coil
                "S" : "c",
                "H" : "a", # helix
                "E" : "b", # sheet
                "G" : "c",
                "B" : "b",
                "T" : "c",
                "C" : "c",
                "X" : "X"} # undefined

def dress_pdb(pdb):

    # molmodel has a method to create a pdb object coming from the mmtf file from RCSB
    from molmodel.io.to_pdb import from_pdb_id as _pdb_from_pdb_id

    tmp_pdb=_pdb_from_pdb_id(pdb.id)

    list_attributes = []
    for pdb_attribute in dir(tmp_pdb):
        if (not callable(getattr(tmp_pdb,pdb_attribute))==True) and (not pdb_attribute.startswith('_')):
            value = getattr(tmp_pdb, pdb_attribute)
            setattr(pdb,pdb_attribute,value)

    pass

