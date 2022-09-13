from sabueso.database.UniProtKB.entry import Entry
from sabueso.database.UniProtKB.entry import Chain, Domain, RegionOfInterest, BindingSite, Ligand,\
        ModifiedResidue, SpliceVariant, SequenceVariant, SequenceConflict, Helix, Turn, Strand, Sequence,\
        Function, CatalyticActivity, ActivityRegulation, Pathway, Subunit, Interaction, Interactant,\
        AlternativeProducts, Isoform, SubCellularLocation, Location, TissueSpecificity, DomainComment, Disease,\
        Similarity, Caution, OnlineInformation, MutagenesisSite, DNABindingRegion, OrganismHost, ShortSequenceMotif,\
        Cofactor, PDB, ZincFingerRegion


from collections import OrderedDict
from sabueso import evidence as evi

def as_list(record):

    if isinstance(record, dict):
        return [record]
    elif isinstance(record, (list, tuple)):
        return record
    else:
        raise ValueError(record, 'is not a dict, not a list')


class trialContextManager:
    def __enter__(self): pass
    def __exit__(self, *args): return True
trial = trialContextManager()


def get_evidence_from_record(value_field, xml_dict_record, xml_dict_evidences, xml_dict_references):
    
    evidence = evi.Evidence()
    
    if isinstance(xml_dict_record, str):
        evidence.value=xml_dict_record    
    if isinstance(xml_dict_record, (list, tuple)):
        evidence.value=xml_dict_record    
    elif isinstance(xml_dict_record, (OrderedDict, dict)):
        if value_field in xml_dict_record:
            evidence.value = xml_dict_record[value_field]
        if '@evidence' in xml_dict_record:
            evidence_numbers_in_db = xml_dict_record['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xml_dict_evidences[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                if 'source' in evidence_in_db:
                   if 'dbReference' in evidence_in_db['source']:
                       dbtype = evidence_in_db['source']['dbReference']['@type']
                       dbid = evidence_in_db['source']['dbReference']['@id']
                       evidence.add_reference({'database':dbtype, 'id':dbid})
   
    return evidence

def get_references_from_record(xml_dict_record, xml_dict_evidences, xml_dict_references):
    
    output = []
    
    if isinstance(xml_dict_record, (OrderedDict, dict)):

        if '@evidence' in xml_dict_record:
            evidence_numbers_in_db = xml_dict_record['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xml_dict_evidences[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                if 'source' in evidence_in_db:
                   if 'dbReference' in evidence_in_db['source']:
                       dbtype = evidence_in_db['source']['dbReference']['@type']
                       dbid = evidence_in_db['source']['dbReference']['@id']
                       output.append(evi.Reference({'database':dbtype, 'id':dbid}))
   
        if '@ref' in xml_dict_record:
            reference_numbers_in_db = xml_dict_record['@ref'].split()
            for reference_number_in_db in reference_numbers_in_db:
                reference_in_db = xml_dict_references[int(reference_number_in_db)-1]
                if reference_in_db['@key']!=reference_number_in_db:
                    raise ValueError('Reference number does not match reference @key')
                if 'citation' in reference_in_db:
                    if reference_in_db['citation']['@type']=='journal article':
                        authors = []
                        for author in reference_in_db['citation']['authorList']['person']:
                            authors.append(author['@name'])
                        pubmed = None
                        doi = None
                        if 'dbReference' in reference_in_db['citation']:
                            for aux_db in reference_in_db['citation']['dbReference']:
                                if aux_db['@type']=='PubMed':
                                    pubmed = evi.Reference({'database':'PubMed', 'id':aux_db['@id']})
                                elif aux_db['@type']=='DOI':
                                    doi = evi.Reference({'database':'DOI', 'id':aux_db['@id']})
                                else:
                                    raise ValueError('Unknown dbReference in Journal article')
                        output.append(evi.Reference({'title': reference_in_db['citation']['title'], 'authors':authors,
                            'journal': reference_in_db['citation']['@name'], 'volume': reference_in_db['citation']['@volume'],
                            'first_page': reference_in_db['citation']['@first'], 'last_page': reference_in_db['citation']['@last'],
                            'pubmed': pubmed, 'doi': doi}))
                    else:
                        raise ValueError('Unknown reference type', reference_in_db['citation']['@type'])
 
    return output

def to_entry(xml_dict):

    entry = Entry()


    # XMLDict shortcuts

    xml_dict_evidences = xml_dict['uniprot']['entry']['evidence']
    xml_dict_references = xml_dict['uniprot']['entry']['reference']
    xml_dict_protein = xml_dict['uniprot']['entry']['protein']
    xml_dict_gene = xml_dict['uniprot']['entry']['gene']
    xml_dict_organism = xml_dict['uniprot']['entry']['organism']
    xml_dict_feature = xml_dict['uniprot']['entry']['feature']
    xml_dict_sequence = xml_dict['uniprot']['entry']['sequence']
    xml_dict_comment = xml_dict['uniprot']['entry']['comment']
    xml_dict_accession = xml_dict['uniprot']['entry']['accession'][0]
    xml_dict_db_reference = xml_dict['uniprot']['entry']['dbReference']

    xml_dict_organism_host = None
    with trial: xml_dict_organism_host = xml_dict['uniprot']['entry']['organismHost']

    this_UniProtKB_reference = evi.Reference({'database':'UniProtKB', 'id':xml_dict_accession})

    ## dataset

    record = xml_dict['uniprot']['entry']['@dataset']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.dataset = evidence

    ## created

    record = xml_dict['uniprot']['entry']['@created']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.created = evidence

    ## modified

    record = xml_dict['uniprot']['entry']['@modified']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.modified = evidence

    ## version

    record = xml_dict['uniprot']['entry']['@version']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.version = evidence

    ## accession

    record = xml_dict['uniprot']['entry']['accession']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.accession = evidence

    ## name

    record = xml_dict['uniprot']['entry']['name']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.name = evidence

    ## protein

    ### recommended_name

    #### full_name

    if 'fullName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['fullName']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.full_name = evidence

    #### short_name

    if 'shortName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['shortName']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.full_name = evidence

    #### ec_number

    if 'ecNumber' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['ecNumber']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.ec_number = evidence

    ### alternative_name

    if 'alternativeName' in xml_dict_protein['recommendedName']:
        for ii in xml_dict_protein['alternativeName']:
            for key, record in ii.items():
                evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
                evidence.add_reference(this_UniProtKB_reference)
                if key == 'fullName':
                    entry.protein.alternative_name.full_name.append(evidence)
                elif key == 'shortName':
                    entry.protein.alternative_name.short_name.append(evidence)

    ## gene

    ### name
            # y si hay mas nombres? que es @type=primary

    if 'name' in xml_dict_gene:
        record = xml_dict_gene['name']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.ec_number = evidence

    ## organism

    ### name
            # y si hay mas tipos de nombres?

    if 'name' in xml_dict_organism:
        for record in as_list(xml_dict_organism['name']):
            evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
            evidence.add_reference(this_UniProtKB_reference)
            if record['@type'] == 'scientific':
                entry.organism.scientific_name=evidence
            elif record['@type'] == 'common':
                entry.organism.common_name=evidence

    ### db_reference
            # y si hay otras dbs que no estoy capturando?

    if isinstance(xml_dict_organism['dbReference'], dict):
        aux_list = [xml_dict_organism['dbReference']]
    else:
        aux_list = xml_dict_organism['dbReference']
    for db_reference in aux_list:
        dbname = db_reference['@type']
        accession = db_reference['@id']
        if dbname=='NCBI Taxonomy':
            entry.organism.NCBI_Taxonomy = evi.Reference({'database':'NCBI Taxonomy', 'id':accession})

    ### lineage

    #### taxon

    if 'taxon' in xml_dict_organism['lineage']:
        record = xml_dict_organism['lineage']['taxon']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.organism.lineage.taxon = evidence

    ## organism_host

    if xml_dict_organism_host is not None:

        entry.organism_host = OrganismHost()

    ### name

        if 'name' in xml_dict_organism_host:
            for record in xml_dict_organism_host['name']:
                evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
                evidence.add_reference(this_UniProtKB_reference)
                if record['@type'] == 'scientific':
                    entry.organism_host.scientific_name=evidence
                elif record['@type'] == 'common':
                    entry.organism_host.common_name=evidence

    ### db_reference

        if isinstance(xml_dict_organism_host['dbReference'], dict):
            aux_list = [xml_dict_organism_host['dbReference']]
        else:
            aux_list = xml_dict_organism_host['dbReference']
        for db_reference in aux_list:
            dbname = db_reference['@type']
            accession = db_reference['@id']
            if dbname=='NCBI Taxonomy':
                entry.organism_host.NCBI_Taxonomy = get_evidence_from_dbreference('NCBI Taxonomy', accession)

    ## reference

    ## comment

    for comment in xml_dict_comment:

        if comment['@type']=='function':
            function = Function()
            if 'text' in comment:
                if '#text' in comment['text']:
                    function.text = comment['text']['#text']
                else:
                    function.text = comment['text']
            function.references = get_references_from_record(comment['text'], xml_dict_evidences, xml_dict_references)
            function.references.append(this_UniProtKB_reference)
            entry.comment.function.append(function)

        elif comment['@type']=='catalytic activity':
            catalytic_activity = CatalyticActivity()
            catalytic_activity.reaction.text = get_evidence_from_record('text', comment['reaction'], xml_dict_evidences, xml_dict_references)
            catalytic_activity.reaction.references = get_references_from_record(comment['reaction'], xml_dict_evidences, xml_dict_references)
            catalytic_activity.reaction.references.append(this_UniProtKB_reference)
            with trial: catalytic_activity.physiological_reaction.direction = get_evidence_from_record('@direction', comment['physiologicalReaction'], xml_dict_evidences, xml_dict_references)
            with trial: catalytic_activity.physiological_reaction.references = get_references_from_record(comment['physiologicalReaction'], xml_dict_evidences, xml_dict_references)
            with trial: catalytic_activity.physiological_reaction.references.append(this_UniProtKB_reference)
            entry.comment.catalytic_activity.append(catalytic_activity)

        elif comment['@type']=='activity regulation':
            activity_regulation = ActivityRegulation()
            activity_regulation.text = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            activity_regulation.references = get_references_from_record(comment['text'], xml_dict_evidences, xml_dict_references)
            activity_regulation.references.append(this_UniProtKB_reference)
            entry.comment.activity_regulation.append(activity_regulation)

        elif comment['@type']=='subunit':
            subunit = Subunit()
            subunit.text = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            subunit.references = get_references_from_record(comment['text'], xml_dict_evidences, xml_dict_references)
            subunit.references.append(this_UniProtKB_reference)
            entry.comment.subunit.append(subunit)
        
        elif comment['@type']=='interaction':
            interaction = Interaction()
            for xml_dict_interactant in comment['interactant']:
                interactant = Interactant()
                interactant.id = xml_dict_interactant['id']
                with trial: interactant.label = xml_dict_interactant['label']
                interactant.intact_id = xml_dict_interactant['@intactId']
                interactant.references.append(this_UniProtKB_reference)
                interaction.interactant.append(interactant)
            interaction.organism_differ = comment['organismsDiffer']
            interaction.experiments = comment['experiments']
            interaction.references.append(this_UniProtKB_reference)
            entry.comment.interaction.append(interaction)
         
        elif comment['@type']=='cofactor':
            cofactor = Cofactor()
            cofactor.name = get_evidence_from_record('name', comment['cofactor'], xml_dict_evidences, xml_dict_references)
            cofactor.text = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            if 'ChEBI'== comment['cofactor']['dbReference']['@type']:
                cofactor.chebi_id = comment['cofactor']['dbReference']['@id']
            entry.comment.cofactor.append(cofactor)
 
        elif comment['@type']=='alternative products':
            alternative_products = AlternativeProducts()
            alternative_products.event = comment['event']['@type']
            for xml_dict_isoform in comment['isoform']:
                isoform = Isoform()
                isoform.id = xml_dict_isoform['id']
                isoform.name = xml_dict_isoform['name']
                if xml_dict_isoform['sequence']['@type']=='described':
                    isoform.vsp_sequence = xml_dict_isoform['sequence']['@ref']
                isoform.references.append(this_UniProtKB_reference)
                alternative_products.isoform.append(isoform)
            alternative_products.references.append(this_UniProtKB_reference)
            entry.comment.alternative_products.append(alternative_products)

        elif comment['@type']=='subcellular location':
            subcellular_location = SubCellularLocation()
            for xml_dict_location in as_list(comment['subcellularLocation']):
                location = Location()
                location.location = get_evidence_from_record('#text', xml_dict_location['location'], xml_dict_evidences, xml_dict_references)
                with trial: location.topology = get_evidence_from_record('#text', xml_dict_location['topology'], xml_dict_evidences, xml_dict_references)
                subcellular_location.location.append(location)
            with trial: subcellular_location = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            subcellular_location.references.append(this_UniProtKB_reference)
            entry.comment.subcellular_location.append(subcellular_location)

        elif comment['@type']=='tissue specificity':
            tissue_specificity = TissueSpecificity()
            tissue_specificity = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            tissue_specificity.references.append(this_UniProtKB_reference)
            entry.comment.tissue_specificity.append(tissue_specificity)

        elif comment['@type']=='domain':
            domain = DomainComment()
            domain = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            domain.references.append(this_UniProtKB_reference)
            entry.comment.domain.append(domain)

        elif comment['@type']=='disease':
            disease = Disease()
            disease.id = comment['disease']['@id']
            disease.name = comment['disease']['name']
            disease.acronym = comment['disease']['acronym']
            disease.description = comment['disease']['description']
            disease.references.append(get_references_from_record(comment['disease'], xml_dict_evidences, xml_dict_references))
            disease.references.append(get_references_from_record(comment, xml_dict_evidences, xml_dict_references))
            disease.references.append(this_UniProtKB_reference)
            entry.comment.disease.append(disease)

        elif comment['@type']=='similarity':
            similarity = Similarity()
            similarity = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            similarity.references.append(this_UniProtKB_reference)
            entry.comment.similarity.append(similarity)

        elif comment['@type']=='caution':
            caution = Caution()
            caution = get_evidence_from_record('#text', comment['text'], xml_dict_evidences, xml_dict_references)
            caution.references.append(this_UniProtKB_reference)
            entry.comment.caution.append(caution)

        elif comment['@type']=='online information':
            online_information = OnlineInformation()
            online_information.name = comment['@name']
            online_information.link = evi.Reference({'web':comment['link']['@uri'], 'name':comment['@name']})
            with trial: online_information.text = comment['text']
            online_information.references.append(this_UniProtKB_reference)
            entry.comment.online_information.append(online_information)



    ## protein existence

    ## keyword

    ## feature

    for feature in xml_dict_feature:

        if feature['@type']=='chain':
            chain = Chain()
            chain.description = feature['@description']
            chain.id=feature['@id']
            chain.begin=feature['location']['begin']['@position']
            chain.end=feature['location']['end']['@position']
            chain.references.append(this_UniProtKB_reference)
            entry.feature.chain.append(chain)

        elif feature['@type']=='domain':
            domain = Domain()
            domain.description = feature['@description']
            domain.begin=feature['location']['begin']['@position']
            domain.end=feature['location']['end']['@position']
            domain.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            domain.references.append(this_UniProtKB_reference)
            entry.feature.domain.append(domain)

        elif feature['@type']=='region of interest':
            region_of_interest = RegionOfInterest()
            region_of_interest.description = feature['@description']
            region_of_interest.begin=feature['location']['begin']['@position']
            region_of_interest.end=feature['location']['end']['@position']
            region_of_interest.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            region_of_interest.references.append(this_UniProtKB_reference)
            entry.feature.region_of_interest.append(region_of_interest)

        elif feature['@type']=='short sequence motif':
            short_sequence_motif = ShortSequenceMotif()
            short_sequence_motif.description = feature['@description']
            short_sequence_motif.begin=feature['location']['begin']['@position']
            short_sequence_motif.end=feature['location']['end']['@position']
            short_sequence_motif.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            short_sequence_motif.references.append(this_UniProtKB_reference)
            entry.feature.short_sequence_motif.append(short_sequence_motif)

        elif feature['@type']=='DNA-binding region':
            dna_binding_region = DNABindingRegion()
            with trial: dna_binding_region.description = feature['@description']
            dna_binding_region.begin=feature['location']['begin']['@position']
            dna_binding_region.end=feature['location']['end']['@position']
            dna_binding_region.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            dna_binding_region.references.append(this_UniProtKB_reference)
            entry.feature.dna_binding_region.append(dna_binding_region)

        elif feature['@type']=='zinc finger region':
            zinc_finger_region = ZincFingerRegion()
            with trial: zinc_finger_region.description = feature['@description']
            zinc_finger_region.begin=feature['location']['begin']['@position']
            zinc_finger_region.end=feature['location']['end']['@position']
            zinc_finger_region.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            zinc_finger_region.references.append(this_UniProtKB_reference)
            entry.feature.zinc_finger_region.append(zinc_finger_region)

        elif feature['@type']=='binding site':
            binding_site = BindingSite()
            with trial: binding_site.begin=feature['location']['begin']['@position']
            with trial: binding_site.end=feature['location']['end']['@position']
            with trial: binding_site.position=feature['location']['position']['@position']
            binding_site.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            binding_site.references.append(this_UniProtKB_reference)
            ligand = Ligand()
            ligand.name = feature['ligand']['name']
            ligand.chebi_id = feature['ligand']['dbReference']['@id']
            with trial: ligand.label = feature['ligand']['label']
            binding_site.ligand=ligand
            entry.feature.binding_site.append(binding_site)

        elif feature['@type']=='modified residue':
            modified_residue = ModifiedResidue()
            modified_residue.description=feature['@description']
            modified_residue.position=feature['location']['position']['@position']
            modified_residue.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            modified_residue.references.append(this_UniProtKB_reference)
            entry.feature.modified_residue.append(modified_residue)

        elif feature['@type']=='splice variant':
            splice_variant = SpliceVariant()
            splice_variant.description=feature['@description']
            splice_variant.id=feature['@id']
            with trial: splice_variant.begin=feature['location']['begin']['@position']
            with trial: splice_variant.end=feature['location']['end']['@position']
            with trial: splice_variant.position=feature['location']['position']['@position']
            splice_variant.original=feature['original']
            splice_variant.variation=feature['variation']
            splice_variant.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            splice_variant.references.append(this_UniProtKB_reference)
            entry.feature.splice_variant.append(splice_variant)

        elif feature['@type']=='sequence variant':
            sequence_variant = SequenceVariant()
            with trial: sequence_variant.description=feature['@description']
            sequence_variant.id=feature['@id']
            sequence_variant.position=feature['location']['position']['@position']
            sequence_variant.original=feature['original']
            sequence_variant.variation=feature['variation']
            sequence_variant.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            sequence_variant.references.append(this_UniProtKB_reference)
            entry.feature.sequence_variant.append(sequence_variant)

        elif feature['@type']=='sequence conflict':
            sequence_conflict = SequenceConflict()
            sequence_conflict.description=feature['@description']
            sequence_conflict.position=feature['location']['position']['@position']
            with trial: sequence_conflict.original=feature['original']
            with trial: sequence_conflict.variation=feature['variation']
            sequence_conflict.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            sequence_conflict.references.append(this_UniProtKB_reference)
            entry.feature.sequence_conflict.append(sequence_conflict)

        elif feature['@type']=='helix':
            helix = Helix()
            helix.begin=feature['location']['begin']['@position']
            helix.end=feature['location']['end']['@position']
            helix.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            helix.references.append(this_UniProtKB_reference)
            entry.feature.helix.append(helix)

        elif feature['@type']=='turn':
            turn = Turn()
            turn.begin=feature['location']['begin']['@position']
            turn.end=feature['location']['end']['@position']
            turn.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            turn.references.append(this_UniProtKB_reference)
            entry.feature.turn.append(turn)

        elif feature['@type']=='strand':
            strand = Strand()
            strand.begin=feature['location']['begin']['@position']
            strand.end=feature['location']['end']['@position']
            strand.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            strand.references.append(this_UniProtKB_reference)
            entry.feature.strand.append(strand)

        elif feature['@type']=='mutagenesis site':
            mutagenesis_site = MutagenesisSite()
            mutagenesis_site.description=feature['@description']
            with trial: mutagenesis_site.position=feature['location']['position']['@position']
            with trial: mutagenesis_site.begin=feature['location']['position']['@begin']
            with trial: mutagenesis_site.end=feature['location']['position']['@end']
            with trial: mutagenesis_site.original=feature['original']
            with trial: mutagenesis_site.variation=feature['variation']
            mutagenesis_site.references = get_references_from_record(feature, xml_dict_evidences, xml_dict_references)
            mutagenesis_site.references.append(this_UniProtKB_reference)
            entry.feature.mutagenesis_site.append(mutagenesis_site)

    ## sequence

    sequence = entry.sequence
 
    sequence.length = xml_dict_sequence['@length']
    sequence.mass = xml_dict_sequence['@mass']
    sequence.checksum = xml_dict_sequence['@checksum']
    sequence.modified = xml_dict_sequence['@modified']
    sequence.version = xml_dict_sequence['@version']
    sequence.text = xml_dict_sequence['#text']
    sequence.references.append(this_UniProtKB_reference)


    # Databases

    record = xml_dict['uniprot']['entry']['@modified']
    evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
    evidence.add_reference(this_UniProtKB_reference)
    entry.modified = evidence
    if 'fullName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['fullName']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.full_name = evidence



    database = entry.database

    for db_reference in xml_dict_db_reference:
        dbname = db_reference['@type']
        accession = db_reference['@id']
        if dbname=='ChEMBL':
            database.ChEMBL = evi.Reference({'database':'ChEMBL', 'id':accession})
        elif dbname=='EC':
            database.EC = evi.Reference({'database':'EC', 'id':accession})
        elif dbname=='DIP':
            database.DIP = evi.Reference({'database':'DIP', 'id':accession})
        elif dbname=='ELM':
            database.ELM = evi.Reference({'database':'ELM', 'id':accession})
        elif dbname=='IntAct':
            database.IntAct = evi.Reference({'database':'IntAct', 'id':accession})
        elif dbname=='BindingDB':
            database.BindingDB = evi.Reference({'database':'BindingDB', 'id':accession})
        elif dbname=='BioGRID':
            database.BioGRID = evi.Reference({'database':'BioGRID', 'id':accession})
        elif dbname=='iPTMnet':
            database.iPTMnet = evi.Reference({'database':'iPTMnet', 'id':accession})
        elif dbname=='MINT':
            database.MINT = evi.Reference({'database':'MINT', 'id':accession})
        elif dbname=='PhosphoSitePlus':
            database.PhosphoSitePlus = evi.Reference({'database':'PhosphoSitePlus', 'id':accession})
        elif dbname=='ProDom':
            database.ProDom = evi.Reference({'database':'ProDom', 'id':accession})
        elif dbname=='ProteinModelPortal':
            database.ProteinModelPortal = evi.Reference({'database':'ProteinModelPortal', 'id':accession})
        elif dbname=='STRING':
            database.STRING = evi.Reference({'database':'STRING', 'id':accession})
        elif dbname=='SMR':
            database.SMR = evi.Reference({'database':'SMR', 'id':accession})
        elif dbname=='PDB':
            pdb = PDB()
            pdb.id = evi.Reference({'database':'PDB', 'id':accession})
            for aux in db_reference['property']:
                if aux['@type']=='method':
                    pdb.method = aux['@value']
                elif aux['@type']=='resolution':
                    pdb.method = aux['@value']
                elif aux['@type']=='chains':
                    pdb.method = aux['@value']
            database.PDB.append(pdb)

    return entry
