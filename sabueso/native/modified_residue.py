from .sabueso_object import SabuesoObject

class ModifiedResidue(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.position = None

    def __repr__(self):

        return f'<ModifiedResidue: {self.description} {self.position}>'
