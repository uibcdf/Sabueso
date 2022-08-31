class Isoform():

    def __init__(self):

        self.type = None
        self.sequence = None
        self.original = None
        self.original_residue_ids = None
        self.variation = None
        self.name = None
        self.length = None
        self.mass = None
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

        self.isoform = {}

        self.binding_site = []
        self.interface = []
        self.ligand = []
        self.interactant = []

        self.references = []

        ### From UniProtKB ###

        from sabueso.database.UniProtKB.uniprot_id import to_entry as uniprot_id_to_entry

        uniprot_entry = uniprot_id_to_entry(uniprot_id)

        for db_alternative_product in uniprot_entry.comment.alternative_products:

            isoform_type = db_alternative_product.event

            if isoform_type == 'alternative splicing':

                aux_vsp_codes = {}

                for db_isoform in db_alternative_product.isoform:

                    isoform = Isoform()

                    isoform.name = db_isoform.name[0]
                    isoform.alternative_name = db_isoform.name[1:]
                    isoform.uniprot_id = db_isoform.id
                    isoform.type = isoform_type
                    aux_vsp_codes[db_isoform.vsp_sequence] = isoform.name

                    self.isoform[isoform.name] = isoform

                for db_splice_variant in uniprot_entry.feature.splice_variant:

                    isoform_name = aux_vsp_codes[db_splice_variant.id]
                    isoform = self.isoform[isoform_name]
                    isoform.original = db_splice_variant.original
                    isoform.variation = db_splice_variant.variation

                    if (db_splice_variant.begin is not None) and (db_splice_variant.end is not None):
                        begin = int(db_splice_variant.begin)
                        end = int(db_splice_variant.end)
                        isoform.original_residue_ids = list(range(begin, end+1))
                    else:
                        raise ValueError('Isoform with position not implemented yet')

                    if db_splice_variant.description != 'In isoform '+isoform_name+'.':
                        raise ValueError('This splice variant is not as expected')

                del(aux_vsp_codes)

        self.isoform['1'].sequence = uniprot_entry.sequence.text 
        self.isoform['1'].length = uniprot_entry.sequence.length
        self.isoform['1'].mass = uniprot_entry.sequence.mass

        for isoform in self.isoform.values():
            if isoform.variation is not None:
                residue_ids = isoform.original_residue_ids
                begin = isoform.original_residue_ids[0]
                end = isoform.original_residue_ids[-1]
                if self.isoform['1'].sequence[begin-1:end]!=isoform.original:
                    raise ValueError('The isoform original segment does not match')
                isoform.sequence = self.isoform['1'].sequence[:begin]+isoform.variation+self.isoform['1'].sequence[end:]
                isoform.length = len(isoform.sequence)

# https://www.uniprot.org/help/alternative_products
