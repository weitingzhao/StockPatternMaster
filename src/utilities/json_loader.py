import json
import random
import string
from datetime import datetime
from pathlib import Path


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class JsonLoader:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self):
        return json.loads(self.file_path.read_bytes())

    def write(self, data: dict):
        self.file_path.write_text(json.dumps(data, indent=3, cls=DateEncoder))

    @staticmethod
    def random_char(length):
        return "".join(random.choices(string.ascii_lowercase) for _ in range(length))

