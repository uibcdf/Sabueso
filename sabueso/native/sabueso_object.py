from pandas import DataFrame

class SabuesoObject():

    def load(self, filename):

        pass

    def to_json(self, filename): # dump to json file

        pass

    def to_dict(self):

        output = {}

        for key in output:
            output[key]=getattr(self, key)

        return output

    def to_pandas_DataFrame(self, with_evidences=True):

        aux_dict = self.to_dict()

        for key in aux_dict:
            aux_dict[key]=[aux_dict[key]]
 
        if not with_evidences:
            for key in aux_dict:
                try:
                    aux_dict[key]=aux_dict[key][0].value
                except:
                    continue
 
        df = DataFrame(aux_dict)

        return df

    def to_jupyter_notebook(self, filename): # save it as a jupyter notebook

        import nbformat as nbf
        from .notebook import notebook

        nb = notebook(self)

        if filename is None:
            filename = f'{self.protein_key_name.value}_function.ipynb'

        with open(filename, 'w') as fff:
            nbf.write(nb, fff)

        return filename

    def to_html(self, filename): # save it as a html page

        pass

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

