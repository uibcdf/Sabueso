class Protein():

    def __init__(self, uniprot_id):


        self.isoform = {}

        self.binding_site = []
        self.interface = []
        self.ligand = []
        self.interactant = []

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

