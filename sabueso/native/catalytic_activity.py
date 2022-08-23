from .sabueso_object import SabuesoObject

class CatalyticActivity(SabuesoObject):

    def __init__(self):

        self.references = []

        self.reaction = None
        self.physiological_direction = None

    def __repr__(self):

        return f'<CatalyticActivity: {self.reaction}>'
