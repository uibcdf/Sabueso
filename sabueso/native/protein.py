from .sabueso_object import SabuesoObject
from sabueso._private.notebook import seq_to_block

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
        self.tissue_specificity = None

        self.function = None
        self.catalytic_activity = None
        self.activity_regulation = None
        self.metabolic_pathways = None

        self.subunit_structure = None
        self.sequence = None
        self.isoforms = []
        self.modified_residues = []
        self.natural_mutations = []
        self.artificial_mutations = []
        self.sequence_conflicts = []
        self.posttranslational_modifications = []

        self.secondary_structure = None
        self.chains = []
        self.domains = []
        self.regions = []
        self.motifs = []
        self.nucleotide_binding_regions = []
        self.dna_binding_regions = []
        self.zinc_finger_regions = []
        self.ca_binding_regions = []
        self.binding_sites = []

        self.interaction = []

        self.diseases = []

        self.ligands = []

        self.uniprot = None
        self.ec = None
        self.chembl = None
        self.biogrid = None
        self.swiss_model = None
        self.dip = None
        self.elm = None
        self.intact = None
        self.mint = None
        self.bindingdb = None
        self.interpro = None
        self.pfam = None
        self.prodom = None
        self.supfam = None
        self.string = None
        self.iptmnet = None
        self.phosphositeplus = None


        self.pdbs = []
        self.segment_in_pdb = {}
 
        self.pdbids100 = None
        self.pdbids95 = None
        self.pdbids75 = None

        self.other_comments = {}

    def __repr__(self):

        return f'<Protein: {self.name.value}, {self.organism.common_name.value}>'

    def notebook(self):

        nb = nbf.v4.new_notebook()

        # Title

        text = f"""\
# **Protein** (*{self.name}, {self.organism.common_name}*)"
"""

        cell_title = nbf.v4.new_markdown_cell(text)

        ## Introduction

        text = f"""\
## ID Data

   - Name: {card.name.value}
   - Key name: {card.key_name.value}
   - Short name: {card.short_name.value if card.short_name is not None else None}
   - Alternative names: {', '.join([ii.value for ii in card.alternative_names])}
   - UniProt Id: {card.uniprot.value}
   - Organism: {card.organism.common_name.value} ({card.organism.scientific_name.value})
"""

        cell_id_data = nbf.v4.new_markdown_cell(text)

        ## Canonical Sequence

        text = f"""\
## Sequence

Canonical ({len(card.sequence)} residues):

```
{seq_to_block(card.sequence.value)}
```
"""

        cell_sequence = nbf.v4.new_markdown_cell(text)

        ###############

        nb['cells'] = [cell_title, cell_id_data, cell_sequence]

        return nb

