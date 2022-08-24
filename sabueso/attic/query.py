
def target(string=None,organism=None):

    from .fields.protein import protein_cards_depuration
    from .DBs.ChEMBL import target_query as ChEMBL_target_query
    from .DBs.UniProt import target_query as UniProt_target_query

    tmp_query_ChEMBL = ChEMBL_target_query(string=string, organism=organism)
    tmp_query_UniProt = UniProt_target_query(string=string, organism=organism)

    tmp_query_all = tmp_query_ChEMBL + tmp_query_UniProt
    tmp_query_all = protein_cards_depuration(tmp_query_all)

    return  tmp_query_all

