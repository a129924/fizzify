from typing import Literal, NamedTuple


class OrderBy(NamedTuple):
    column_name: str
    direction: Literal["asc", "desc"]
