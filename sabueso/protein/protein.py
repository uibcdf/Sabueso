
class Isoform():

    def __init__(self):

        self.type = None
        self.sequence = None
        self.differences_from_canonical = None
        self.name = None
        self.alternative_name = []
        self.uniprot_id = None
        self.pdb_id = None
        self.references = []

class BindingSite():

    def __init__(self):

        self.ligand = None
        self.residue_ids = []
        self.pdbi_id = []
        self.references = []

class Ligand():

    def __init__(self):

        self.chebi_id = None
        self.binding_site = []
        self.pdbi_id = []
        self.references = []

class Interface():

    def __init__():

        self.interactant = None
        self.residue_ids = []
        self.pdbi_id = []
        self.references = []

class Interactant():

    def __init__():

        self.uniprot_id = None
        self.interface = []
        self.pdbi_id = []
        self.references = []

class Residue():

    def __init__(self):

        self.id = None
        self.chain_id = None
        self.ligand = []
        self.binding_site = []
        self.interactant = []
        self.interface = []

class Protein():

    def __init__(self, uniprot_id):

        self.uniprot_id = None

        self.isoform = []

        self.binding_site = []
        self.interface = []
        self.ligand = []
        self.interactant = []

        self.references = []

        ### From UniProtKB ###

        from sabueso.database.UniProtKB.uniprot_id import to_entry as uniprot_id_to_entry

        self.uniprot_entry = uniprot_id_to_entry(uniprot_id)

