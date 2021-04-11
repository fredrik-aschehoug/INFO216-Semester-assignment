import json
from typing import List, Tuple, Union, Generator
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import OWL

from models.namespaces import p, schema, skos, wd, wds, wdt, wdtn, wikibase, yago3
from models.types import rdf_node


GET_ENTITIES_QUERY = """
SELECT DISTINCT ?entity
WHERE {
    ?subject nhterm:hasEntity ?entity .
}
"""


class GraphService():
    """Service which contains the rdflib graph and some helper methods related to graph operations."""
    def __init__(self, graph, notation):
        self._notation = notation
        self._graph = self._parse_input(graph, notation)

        # Bind namespaces
        self._graph.bind("owl", OWL)
        self._graph.bind("yago3", yago3)
        self._graph.bind("wd", wd)
        self._graph.bind("wdt", wdt)
        self._graph.bind("wdtn", wdtn)
        self._graph.bind("wikibase", wikibase)
        self._graph.bind("wds", wds)
        self._graph.bind("p", p)
        self._graph.bind("schema", schema)
        self._graph.bind("skos", skos)

    @staticmethod
    def _parse_input(raw: Union[str, object], notation: str) -> Graph:
        g = Graph()

        if (notation == "json-ld"):
            g.parse(data=json.dumps(raw), format=notation)
        else:
            g.parse(data=raw, format=notation)
        return g

    @property
    def notation(self) -> Graph:
        return self._notation

    @property
    def graph(self) -> Graph:
        """Return current rdflib Graph object"""
        return self._graph

    @graph.setter
    def graph(self, g: Graph) -> None:
        """Set current rdflib Graph object"""
        self._graph = g

    def get_graph_serialized(self, notation: str = None) -> str:
        """Return a serialized version of the graph."""
        if (notation is None):
            notation = self._notation
        return self._graph.serialize(format=notation).decode("utf-8")

    def get_entities(self) -> Generator[str, None, None]:
        """Generator which yields all entity URIs in the graph"""
        qres = self._graph.query(GET_ENTITIES_QUERY)

        for (entity,) in qres:
            yield str(entity)

    def add(self, triple: tuple) -> None:
        """Add a triple to the graph."""
        self._graph.add(triple)

    @staticmethod
    def create_node(node: dict) -> rdf_node:
        """Convert a SPARQL result dictionary to an rdflib node."""
        if (node["type"] == "uri"):
            return URIRef(node["value"])

        if (node["type"] == "literal"):
            if ("datatype" in node):
                return Literal(node["value"], datatype=URIRef(node["datatype"]))
            return Literal(node["value"])

        if (node["type"] == "bnode"):
            return BNode(node["value"])

    def create_triple(self, triple: dict) -> Tuple[rdf_node, rdf_node, rdf_node]:
        """Convert a SPARQL result row to rdflib nodes in a tuple, ready to be added to the graph."""
        return (self.create_node(triple["subject"]), self.create_node(triple["predicate"]), self.create_node(triple["object"]))
