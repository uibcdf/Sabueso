from .sabueso_object import SabuesoObject

class AlternativeSequence(SabuesoObject):

    def __init__(self):

        self.references = []

        self.type = None
        self.name = None
        self.intact = None
        self.uniprot = None
        self.mutations = None
        self.isoform_specific = None

    def __repr__(self):

        return f'<AlternativeSequence: self.name>'

