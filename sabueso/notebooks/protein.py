import nbformat as nbf

def _seq_to_block(sequence, length=80):

    output = ''

    for ii in range(0, len(sequence), length):
        output += sequence[ii:length+ii]+'\n'

    return output

def protein_notebook(card):

    nb = nbf.v4.new_notebook()

    # Title

    text = f"# **Protein Card** (*{card.name.value}, {card.organism.common_name.value}*)"

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
{_seq_to_block(card.sequence.value)}
```
"""

    cell_sequence = nbf.v4.new_markdown_cell(text)



    ###############

    nb['cells'] = [cell_title, cell_id_data, cell_sequence]

    return nb
