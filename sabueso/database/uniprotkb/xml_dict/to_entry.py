from sabueso.database.uniprotkb.entry import Entry
from collections import OrderedDict
from evidence import Evidence

def to_entry(xmldict):

    entry = Entry()

    # XMLDict shortcuts

    xmldict_evidence = xmldict['uniprot']['entry']['evidence']
    xmldict_protein = xmldict['uniprot']['entry']['protein']

    xmldict_accession = xmldict['uniprot']['entry']['accession'][0]

    # Protein

    protein = entry.protein

    # Recommended Name

    evidence = Evidence()

    xmldict_full_name = xmldict_protein['recommendedName']['fullName']

    if isinstance(xmldict_full_name, str):
        evidence.value=xmldict_full_name
    elif isinstance(xmldict_full_name, OrderedDict):
        if '#text' in xmldict_full_name:
            evidence.value = xmldict_full_name['#text']
        if '@evidence' in xmldict_full_name:
            evidence_numbers_in_db = xmldict_full_name['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xmldict_evidence[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                _add_reference_to_evidence(evidence, evidence_in_db)

    evidence.add_reference({'database':'UniProtKB', 'id':xmldict_accession})

    protein.recommended_name.full_name = evidence

    return entry
