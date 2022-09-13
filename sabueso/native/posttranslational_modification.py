from .sabueso_object import SabuesoObject

class PostTranslationalModification(SabuesoObject):

    def __init__(self):

        self.references = []

        self.modified_residues = None
        self.cross_link = None

    def __repr__(self):

        return f'<PostTranslationalModification: >'
