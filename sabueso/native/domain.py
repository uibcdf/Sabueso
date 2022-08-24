from .sabueso_object import SabuesoObject

class Domain(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.begin = None
        self.end = None
        self.note = None

    def __repr__(self):

        return f'<Domain: {self.description} {self.begin}-{self.end}>'
