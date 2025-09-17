from typing import Tuple

def get_pagination(limit: int = 50, offset: int = 0, max_limit: int = 200) -> Tuple[int, int]:
    if limit < 1: limit = 1
    if limit > max_limit: limit = max_limit
    if offset < 0: offset = 0
    return limit, offset
