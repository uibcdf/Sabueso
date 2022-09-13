from .sabueso_object import SabuesoObject

class CaBindingRegion(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.begin = None
        self.end = None

    def __repr__(self):

        return f'<CaBindingRegion: {self.description} {self.begin}-{self.end}>'
