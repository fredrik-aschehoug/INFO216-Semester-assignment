from rdflib import URIRef, Literal
from typing import Union, List, Dict


rdf_node = Union[Literal, URIRef]

uri_map = Dict[str, str]
uri_maps = List[uri_map]

sparql_bindings = List[Dict[str, str]]
