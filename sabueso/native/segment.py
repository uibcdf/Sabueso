from .sabueso_object import SabuesoObject

class Segment(SabuesoObject):

    def __init__(self):

        self.references = []

        self.begin = None
        self.end = None
        self.length = None
        self.chain = None
        self.entity = None

    def __repr__(self):

        return f'<Segment: >'
