

class CsvLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        with open(self.path, 'r') as file:
            return file.read()