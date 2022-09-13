from .sabueso_object import SabuesoObject

class Function(SabuesoObject):

    def __init__(self):

        self.references = []

        self.description = None
        self.begin = None
        self.end = None

    def show(self):

        import nbformat as nbf
        from .notebook import notebook

        nb = notebook(self)

        from IPython.display import display, HTML, Markdown, Latex

        for cell in nb['cells']:
            if cell['cell_type']=='markdown':
                display(Markdown(cell['source']))
            elif cell['cell_type']=='code':
                print('The notebook has cells with code')
            else:
                print('Cell type note recognized')
        pass

    def to_jupyter_notebook(self, filename=None):

        import nbformat as nbf
        from .notebook import notebook

        nb = notebook(self)

        if filename is None:
            filename = f'{self.protein_key_name.value}_function.ipynb'

        with open(filename, 'w') as fff:
            nbf.write(nb, fff)

        return filename


    def __repr__(self):

        return f'<Function: {self.protein_key_name}>'

    def notebook(self):

        nb = nbf.v4.new_notebook()

        # Title

        text = f"""\
# **Function** (*{card.protein_name.value}, {card.organism_common_name.value}*)
"""

        cell_title = nbf.v4.new_markdown_cell(text)

        ## Uniprot function

        text = f"""\
### UniProtKB function

{card.uniprot_function}

{card.notes}

{card.references}
"""

        cell_uniprot_function = nbf.v4.new_markdown_cell(text)

        ###############

        nb['cells'] = [cell_title, cell_uniprot_function]

        return nb

