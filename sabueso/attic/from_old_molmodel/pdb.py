from .atom import Atom
from .group import Group
from .bioassembly import BioAssembly
from copy import deepcopy as _deepcopy

class PDB:

    def __init__(self):

        self.id = None
        self.method = None
        self.resolution = None
        self.title = None
        self.deposition_date = None
        self.unit_cell = None
        self.num_models = 0

        self.bioassembly = []
        self.chain = []
        self.entity = []
        self.segment = []
        self.group = []
        self.atom = []
        self.bond = []

        self.num_bioassemblies = 0
        self.num_chains = 0
        self.num_entities = 0
        self.num_segments = 0
        self.num_groups = 0
        self.num_atoms = 0
        self.num_bonds = 0

        self.ion = []
        self.water = []
        self.small_molecule = []
        self.protein = []
        self.peptide = []
        self.dna = []
        self.rna = []

        self.num_ions = 0
        self.num_waters = 0
        self.num_small_molecules = 0
        self.num_proteins = 0
        self.num_peptides = 0
        self.num_dnas = 0
        self.num_rnas = 0

        self.coordinates=[]
        self.bfactors=[]

