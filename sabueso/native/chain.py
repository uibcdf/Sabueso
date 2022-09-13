from .sabueso_object import SabuesoObject

class Chain(SabuesoObject):

    def __init__(self):

        self.references = []

        self.protein_name = None
        self.description = None
        self.index = None
        self.uniprot_chain_id = None
        self.begin = None
        self.end = None

    def __repr__(self):

        return f'<Chain: {self.protein_name} {self.begin}-{self.end}>'

