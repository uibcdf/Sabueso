
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

class Chain():

    def __init__(self):

        self.description = None
        self.id = None
        self.begin = None
        self.end = None
        self.references = []

class Domain():

    def __init__(self):

        self.description = None
        self.begin = None
        self.end = None
        self.references = []

class RegionOfInterest():

    def __init__(self):

        self.description = None
        self.begin = None
        self.end = None
        self.references = []

class Ligand():

    def __init__(self):

        self.name = None
        self.chebi_id = None
        self.label = None

class BindingSite():

    def __init__(self):

        self.begin = None
        self.end = None
        self.position = None
        self.ligand = None
        self.references = []

class ModifiedResidue():

    def __init__(self):

        self.description = None
        self.position = None
        self.references = []

class SpliceVariant():

    def __init__(self):

        self.id = None
        self.description = None
        self.original = None
        self.variation = None
        self.begin = None
        self.end = None
        self.references = []

class SequenceVariant():

    def __init__(self):

        self.id = None
        self.description = None
        self.original = None
        self.variation = None
        self.position = None
        self.references = []

class SequenceConflict():

    def __init__(self):

        self.id = None
        self.description = None
        self.original = None
        self.variation = None
        self.position = None
        self.references = []

class Feature():

    def __init__(self):

        self.chain = []
        self.domain = []
        self.region_of_interest = []
        self.binding_site = []
        self.modified_residue = []
        self.splice_variant = []
        self.sequence_variant = []
        self.sequence_conflict = []

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
        self.feature = Feature()

        self.database = Database()
