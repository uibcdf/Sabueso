
class RecommendedName():

    def __init__(self):

        self.full_name = None
        self.ec_number = None

class Protein():

    def __init__(self):

        self.recommended_name = RecommendedName()

class Entry():

    def __init__(self):

        self.dataset = None
        self.created = None
        self.modified = None
        self.version = None

        self.accession = []

        self.name = None

        self.protein = Protein()

