from .sabueso_object import SabuesoObject

class SecondaryStructure():

    def __init__(self):

        self.references = []

        self.description = None
        self.helices = []
        self.strands = []
        self.turns = []

    def __repr__(self):

        return f'<SecondaryStructureCard: {len(self.helices)} helices, {len(self.strands)} strands and {len(self.turns)} turns>'
