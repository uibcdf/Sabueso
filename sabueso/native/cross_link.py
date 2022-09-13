from .sabueso_object import SabuesoObject

class CrossLink(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.begin = None
        self.end = None

    def __repr__(self):

        return f'<CrossLink: {self.begin}-{self.end}>'

