from .sabueso_object import SabuesoObject

class NucleotideBindingRegion():

    def __init__(self):

        self.references = []

        self.nucleotide = None
        self.begin = None
        self.end = None

    def __repr__(self):

        return f'<NucleotideBindingRegion: {self.nucleotide} {self.begin}-{self.end}>'
