from .sabueso_object import SabuesoObject

class Protein(SabuesoObject):

    def __init__(self):

        self.references = []

        self.name = None
        self.key_name = None
        self.short_name = None
        self.uniprot_entry_name = None
        self.alternative_names = None
        self.family = None
        self.organism = None
        self.host = None
        self.location_in_cell = None
        self.

    def __repr__(self):

        return f'<ZincFingerRegion: {self.description} {self.begin}-{self.end}>'
