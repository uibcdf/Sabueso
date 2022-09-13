from .sabueso_object import SabuesoObject

class PDB(SabuesoObject):

    def __init__(self):

        self.references = []

        self.pdb_id = None

    def __repr__(self):

        return f'<PDB: {self.pdb_id}>'
