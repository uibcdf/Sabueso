from .sabueso_object import SabuesoObject

class Helix():

    def __init__(self):

        self.references = []

        self.description = None
        self.begin = None
        self.end = None

    def __repr__(self):

        return f'<Helix: {self.description} {self.begin}-{self.end}>'
