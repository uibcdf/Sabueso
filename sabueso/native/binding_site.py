from .sabueso_object import SabuesoObject

class BindingSite(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.position = None

    def __repr__(self):

        return f'<BindingSite: {self.description} {self.position}>'
