import json
import random
import string
from pathlib import Path
from datetime import datetime
from typing import Any, List, Tuple, Optional

# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, datetime):
#             return obj.isoformat()
#         return super().default(obj)
#
#
# def load_json(file_path: Path):
#     with open(file_path, "r") as f:
#         return json.load(f)
#
#
# def write_json(file_path: Path, data: dict):
#     with open(file_path, "w") as f:
#         file_path.write_text(json.dumps(data, indent=3, cls=DateEncoder))
#
