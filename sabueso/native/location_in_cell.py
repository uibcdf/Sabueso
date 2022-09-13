from .sabueso_object import SabuesoObject

class LocationInCell(SabuesoObject):

    def __init__(self):

        self.references = []

        self.location = []
        self.node = None

    def __repr__(self):

        return f'<LocationInCell: {self.location}>'
