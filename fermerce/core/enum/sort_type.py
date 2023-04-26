from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SearchType(str, Enum):
    _and = "and"
    _or = "or"
