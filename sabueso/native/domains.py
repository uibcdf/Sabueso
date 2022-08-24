from .sabueso_object import SabuesoObject

class Domains(SabuesoObject):

    def __init__(self):

        self.references = []

        self.protein_name = None
        self.protein_keyname = None
        self.protein_uniprot_id = None

        self.domain = []
        self.notes = None

        self.interpro_id = None
        self.panther_id = None
        self.pfam_id = None
        self.supfam_id = None
        self.prosite_id = None

    def __repr__(self):

        return f'<Domains: {len(self.domain)} domains>'
