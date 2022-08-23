from .sabueso_object import SabuesoObject

class Interactant(SabuesoObject):

    def __init__(self):

        self.references = []

        self.type = None
        self.name = None
        self.intact = None
        self.uniprot = None
        self.mutations = None
        self.isoform_specific = None

    def __repr__(self):

        if self.name is not None:
            return f'<Interactant: {self.type}, {self.name}>'
        elif self.intact is not None:
            return f'<Interactant: {self.type}, {self.intact}>'
        else:
            return f'<Interactant: unknown>'

