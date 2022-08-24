
class RecommendedName():

    def __init__(self):

        self.full_name = None
        self.short_name = None
        self.ec_number = None

class AlternativeName():

    def __init__(self):

        self.full_name = []
        self.short_name = []

class Gene():

    def __init__(self):

        self.name = None

class Lineage():

    def __init__(self):

        self.taxon = None

class Organism():

    def __init__(self):

        self.scientific_name = None
        self.common_name = None
        self.lineage = Lineage()
        self.NCBI_Taxonomy = None

class Database():

    def __init__(self):

        self.ChEMBL = None
        self.EC = None
        self.DIP = None
        self.ELM = None
        self.IntAct = None
        self.BindingDB = None
        self.BioGRID = None
        self.iPTMnet = None
        self.MINT = None
        self.PhosphoSitePlus = None
        self.ProDom = None
        self.ProteinModelPortal = None
        self.STRIG = None
        self.SMR = None

class Protein():

    def __init__(self):

        self.recommended_name = RecommendedName()
        self.alternative_name = AlternativeName()


class Entry():

    def __init__(self):

        self.dataset = None
        self.created = None
        self.modified = None
        self.version = None
        self.accession = []
        self.name = None

        self.protein = Protein()
        self.gene = Gene()
        self.organism = Organism()

        self.database = Database()
