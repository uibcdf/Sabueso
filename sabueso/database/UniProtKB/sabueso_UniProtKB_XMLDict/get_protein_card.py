def get_protein_card(item):

    from sabueso.cards import ProteinCard
    from sabueso.cards import OrganismCard
    from .get_name import get_name
    from .get_key_name import get_key_name
    from .get_short_name import get_short_name
    from .get_uniprot_entry_name import get_uniprot_entry_name
    from .get_alternative_names import get_alternative_names
    from .get_organism import get_organism
    from .get_host import get_host
    from .get_location_in_cell import get_location_in_cell
    from .get_tissue_specificity import get_tissue_specificity
    from .get_function import get_function
    from .get_catalytic_activity import get_catalytic_activity
    from .get_activity_regulation import get_activity_regulation
    from .get_metabolic_pathways import get_metabolic_pathways
    from .get_diseases import get_diseases
    from .get_canonical_sequence import get_canonical_sequence
    from .get_isoforms import get_isoforms
    from .get_modified_residues import get_modified_residues
    from .get_natural_mutations import get_natural_mutations
    from .get_artificial_mutations import get_artificial_mutations
    from .get_sequence_conflicts import get_sequence_conflicts
    from .get_chains import get_chains
    from .get_domains import get_domains
    from .get_regions import get_regions
    from .get_motifs import get_motifs
    from .get_nucleotide_binding_regions import get_nucleotide_binding_regions
    from .get_dna_binding_regions import get_dna_binding_regions
    from .get_zinc_finger_regions import get_zinc_finger_regions
    from .get_ca_binding_regions import get_ca_binding_regions
    from .get_binding_sites import get_binding_sites
    from .get_uniprot import get_uniprot
    from .get_ec import get_ec
    from .get_dbreference import get_dbreference
    from .get_interactions import get_interactions
    from .get_subunit_structure import get_subunit_structure
    from .get_secondary_structure import get_secondary_structure
    from .get_domain_comments import get_domain_comments
    from .get_sequence_similarity import get_sequence_similarity

    card = ProteinCard()

    # Names
    card.name = get_name(item)
    card.key_name = get_key_name(item)
    card.short_name = get_short_name(item)
    card.uniprot_entry_name = get_uniprot_entry_name(item)
    card.alternative_names = get_alternative_names(item)

    # Family
    card.family = get_sequence_similarity(item)

    # Location and expression
    card.organism = get_organism(item, as_card=True)
    card.host = get_host(item)
    card.location_in_cell = get_location_in_cell(item, as_cards=True)
    card.tissue_specificity = get_tissue_specificity(item)

    # Function
    card.function = get_function(item)
    card.catalytic_activity = get_catalytic_activity(item)
    card.activity_regulation = get_activity_regulation(item)
    card.metabolic_pathways = get_metabolic_pathways(item)

    # Sequence
    card.sequence = get_canonical_sequence(item)
    card.isoforms = get_isoforms(item, as_cards=True)
    card.modified_residues = get_modified_residues(item, as_cards=True)
    card.natural_mutations = get_natural_mutations(item, as_cards=True)
    card.artificial_mutations = get_artificial_mutations(item, as_cards=True)
    card.sequence_conflicts = get_sequence_conflicts(item, as_cards=True)

    # Structure
    card.subunit_structure = get_subunit_structure(item)
    card.secondary_structure = get_secondary_structure(item, as_cards=True)
    card.chains = get_chains(item, as_cards=True)
    card.domains = get_domains(item, as_cards=True)
    card.regions = get_regions(item, as_cards=True)
    card.motifs = get_motifs(item, as_cards=True)
    card.nucleotide_binding_regions = get_nucleotide_binding_regions(item, as_cards=True)
    card.dna_binding_regions = get_dna_binding_regions(item, as_cards=True)
    card.zinc_finger_regions = get_zinc_finger_regions(item, as_cards=True)
    card.ca_binding_regions = get_ca_binding_regions(item, as_cards=True)
    card.binding_sites = get_binding_sites(item, as_cards=True)

    # Diseases
    card.diseases = get_diseases(item, as_cards=True)

    # Interactions
    card.interactions = get_interactions(item, as_cards=True)

    # Other comments
    card.other_comments['domain']= get_domain_comments(item)

    # Databases
    card.uniprot =get_uniprot(item)
    card.ec = get_ec(item)
    card.chembl = get_dbreference(item, dbname='ChEMBL')
    card.biogrid = get_dbreference(item, dbname='BioGRID')
    card.swiss_model = get_dbreference(item, dbname='SMR')
    card.dip = get_dbreference(item, dbname='DIP')
    card.elm = get_dbreference(item, dbname='ELM')
    card.intact = get_dbreference(item, dbname='IntAct')
    card.mint = get_dbreference(item, dbname='MINT')
    card.bindingdb = get_dbreference(item, dbname='BindingDB')
    card.prodom = get_dbreference(item, dbname='ProDom')
    card.string = get_dbreference(item, dbname='STRIM')
    card.iptmnet = get_dbreference(item, dbname='iPTMnet')
    card.phosphositeplus = get_dbreference(item, dbname='PhosphoSitePlus')

    #card.pdbs = get_pdbs(item)

    return card

