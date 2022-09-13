from .sabueso_object import SabuesoObject

class Disease(SabuesoObject):

    def __init__(self):

        self.references = []

        self.name = None
        self.acronym = None
        self.description = None
        self.note = None
        self.proteins_involved = None

    def __repr__(self):

        return f'<Disease: {self.name}>'
