import json

from datetime import datetime
from pathlib import Path


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class JsonLoader:

    def __init__(self, path: Path):
        self.Path = path

    def is_file(self):
        return self.Path.is_file()

    def load(self):
        return json.loads(self.Path.read_bytes())

    def save(self, data: object):
        self.Path.write_text(json.dumps(data, indent=3, cls=DateEncoder))



