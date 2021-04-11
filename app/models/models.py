from pydantic import BaseModel
from typing import Union


# TODO: graph param should be union of str and JSON obj
class Item(BaseModel):
    graph: Union[str]
    notation: str
