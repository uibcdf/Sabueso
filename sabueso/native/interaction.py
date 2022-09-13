from .sabueso_object import SabuesoObject

class Interaction(SabuesoObject):

    def __init__(self):

        self.references = []

        self.interactants = []
        self.n_experiments = None
        self.same_organism = None
        self.intact = None
        self.imex = None
        self.with_mutations = None

    def __repr__(self):

        return f'<Interaction: {self.interactants}>'
