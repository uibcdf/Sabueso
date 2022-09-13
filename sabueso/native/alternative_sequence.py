from .sabueso_object import SabuesoObject

class AlternativeSequence(SabuesoObject):

    def __init__(self):

        self.references = []

        self.begin = None
        self.end = None
        self.description = None

    def __repr__(self):

        return f'<AlternativeSequence: {self.description} {self.begin}-{self.end}>'

