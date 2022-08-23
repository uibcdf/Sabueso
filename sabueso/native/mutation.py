from .sabueso_object import SabuesoObject

class Mutation(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.position = None
        self.original = None
        self.variation = None

    def __repr__(self):

        return f'<Mutation: {self.original}{self.position}{self.variation}>'
