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
 
        df = DataFrame(aux_dict, index =[self.position])

        return df

    def to_jupyter_notebook(self, filename): # save it as a jupyter notebook

        pass

    def to_html(self, filename): # save it as a html page

        pass

