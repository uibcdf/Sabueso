from .sabueso_object import SabuesoObject

class Isoform(SabuesoObject):

    def __init__(self):

        self.references = []

        self.name = None
        self.alternative_names = None
        self.type = None
        self.sequence = None
        self.begin = None
        self.end = None
        self.original = None
        self.variation = None
        self.vsp = None
        self.uniprot = None

    def __repr__(self):

        return f'<Isoform: {self.name}>'
