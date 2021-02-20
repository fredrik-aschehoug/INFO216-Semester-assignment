from pydantic import BaseModel
from typing import Union
from rdflib import URIRef, Literal


# TODO: graph param should be union of str and JSON obj
class Item(BaseModel):
    graph: Union[str]
    notation: str


rdf_node = Union[Literal, URIRef]
