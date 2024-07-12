import pandas as pd
from io import StringIO

from pandas import DataFrame


class CsvLoader:
    def __init__(self, path):
        self.path = path
        if not self.path.exists():
            # Create any necessary parent directories
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Create the file
            self.path.touch()

    def load(self):
        if not self.path.exists():
            return None
        return pd.read_csv(self.path)

    def save_str(self, data: str):
        df = pd.read_csv(StringIO(data), header=None)  # Create DataFrame
        df.to_csv(self.path, index=False, header=False)  # Save to CSV

    def save_df(self, df: DataFrame):
        df.to_csv(self.path, index=False, header=False)  # Save to CSV

