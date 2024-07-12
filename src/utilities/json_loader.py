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
        self.path = path

    def load(self):
        return json.loads(self.path.read_bytes())

    def save(self, data: object):
        self.path.write_text(json.dumps(data, indent=3, cls=DateEncoder))



