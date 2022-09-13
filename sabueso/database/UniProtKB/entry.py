
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

class OrganismHost():

    def __init__(self):

        self.scientific_name = None
        self.common_name = None
        self.NCBI_Taxonomy = None

class PDB():

    def __init__(self):

        self.id = None
        self.method = None
        self.resolution = None
        self.chains = None

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
        self.PDB = []

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

class DNABindingRegion():

    def __init__(self):

        self.description = None
        self.begin = None
        self.end = None
        self.references = []

class ZincFingerRegion():

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
        self.position = None
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

        self.description = None
        self.original = None
        self.variation = None
        self.position = None
        self.references = []

class ShortSequenceMotif():

    def __init__(self):

        self.description = None
        self.begin = None
        self.end = None
        self.references = []

class MutagenesisSite():

    def __init__(self):

        self.description = None
        self.position = None
        self.begin = None
        self.end = None
        self.original = None
        self.variation = None
        self.references = []

class Helix():

    def __init__(self):

        self.begin = None
        self.end = None
        self.references = []

class Turn():

    def __init__(self):

        self.begin = None
        self.end = None
        self.references = []

class Strand():

    def __init__(self):

        self.begin = None
        self.end = None
        self.references = []

class Feature():

    def __init__(self):

        self.chain = []
        self.domain = []
        self.region_of_interest = []
        self.dna_binding_region = []
        self.zinc_finger_region = []
        self.binding_site = []
        self.modified_residue = []
        self.splice_variant = []
        self.sequence_variant = []
        self.sequence_conflict = []
        self.short_sequence_motif = []
        self.mutagenesis_site = []
        self.helix = []
        self.turn = []
        self.strand = []

class Sequence():

    def __init__(self):

        self.length = None
        self.mass = None
        self.checksum = None
        self.modified = None
        self.version = None
        self.text = None
        self.references = []

class Function():

    def __init__(self):

        self.text = None
        self.references = []

class CatalyticActivity():

    def __init__(self):

        self.reaction = Reaction()
        self.physiological_reaction = PhysiologicalReaction()

class Reaction():

    def __init__(self):

        self.text = None
        self.references = []

class PhysiologicalReaction():

    def __init__(self):

        self.direction = None
        self.references = []

class ActivityRegulation():

    def __init__(self):

        self.text = None
        self.references = []

class Pathway():

    def __init__(self):

        self.text = None
        self.references = []

class Subunit():

    def __init__(self):

        self.text = None
        self.references = []

class Interaction():

    def __init__(self):

        self.interactant = []
        self.organism_differ = None
        self.experiments = None
        self.references = []

class Interactant():

    def __init__(self):

        self.id = None
        self.label = None
        self.intact_id = None
        self.references = []

class Cofactor():

    def __init__(self):

        self.name = None
        self.text = None
        self.chebi_id = None
        self.references = []

class Isoform():

    def __init__(self):

        self.id = None
        self.name = None
        self.vsp_sequence = None
        self.references = []

class AlternativeProducts():

    def __init__(self):

        self.event = None
        self.isoform = []
        self.references = []

class Location():

    def __init__(self):

        self.location = None
        self.topology = None
        self.references = []

class SubCellularLocation():

    def __init__(self):

        self.location = []
        self.text = None
        self.references = []

class TissueSpecificity():

    def __init__(self):

        self.text = None
        self.references = []

class DomainComment():

    def __init__(self):

        self.text = None
        self.references = []

class Disease():

    def __init__(self):

        self.name = None
        self.id = None
        self.acronym = None
        self.description = None
        self.text = None
        self.references = []

class Similarity():

    def __init__(self):

        self.text = None
        self.references = []

class Caution():

    def __init__(self):

        self.text = None
        self.references = []

class OnlineInformation():

    def __init__(self):

        self.name = None
        self.text = None
        self.link = None
        self.references = []

class Comment():

    def __init__(self):

        self.function = []
        self.catalytic_activity = []
        self.activity_regulation = []
        self.pathway = []
        self.subunit = []
        self.interaction = []
        self.cofactor = []
        self.alternative_products = []
        self.subcellular_location = []
        self.tissue_specificity = []
        self.domain = []
        self.disease = []
        self.similarity = []
        self.caution = []
        self.online_information = []

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
        self.organism_host = OrganismHost()
        self.feature = Feature()
        self.sequence = Sequence()
        self.comment = Comment()
        self.database = Database()

