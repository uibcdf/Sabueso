from .sabueso_object import SabuesoObject

class Organism():

    def __init__(self):

        self.references = []

        self.common_name = None
        self.scientific_name = None
        self.ncbi_taxonomy = None

    def __repr__(self):

        return f'<Organism: {self.common_name.value}>'
