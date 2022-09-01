class ProteinCard():

    def __init__(self):

        self.full_name = None
        self.short_name = None
        self.alternative_names = []

        self.sequence = None
        self.length = None
        self.mass = None

        self.isoforms = {}



        self.binding_sites = []
        self.interfaces = []
        self.ligands = []
        self.interactants = []


        self.database = ProteinDataBasesCard()

        self.references = []

class ProteinDataBasesCard():

    def __init__(self):

        self.BindingDB = None
        self.BioGRID = None
        self.ChEMBL = None
        self.DIP = None
        self.EC = None
        self.ELM = None
        self.IntAct = None
        self.iPTMnet = None
        self.MINT = None
        self.PhosphoSitePlus = None
        self.ProDom = None
        self.ProteinModelPortal = None
        self.SMR = None
        self.STRING = None
        self.UniProtKB = None

