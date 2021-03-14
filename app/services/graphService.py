from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import OWL
import json
from typing import Union, List, Tuple
from models.models import rdf_node
from models.namespaces import yago3, wd, p, wdt, schema, wdtn, wikibase, skos, wds


class GraphService():

    def __init__(self, graph, notation):
        self._notation = notation
        self._graph = self.parse_input(graph, notation)
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
    def parse_input(raw: Union[str, object], notation: str) -> Graph:
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
    def graph(self, g):
        """Set current rdflib Graph object"""
        self._graph = g

    def get_graph_serialized(self, notation: str = None) -> str:
        if (notation is None):
            notation = self._notation
        return self._graph.serialize(format=notation).decode("utf-8")

    def get_entities(self) -> List[str]:
        """Run query against internal graph and return list of entity URIs"""
        qres = self._graph.query(
            """SELECT DISTINCT ?entity
        WHERE {
            ?subject nhterm:hasEntity ?entity .
        }""")

        entities = set([str(entity) for (entity,) in qres])
        return list(entities)

    def add(self, triple: tuple):
        self._graph.add(triple)

    @staticmethod
    def create_node(node: dict) -> rdf_node:
        if (node["type"] == "uri"):
            return URIRef(node["value"])

        if (node["type"] == "literal"):
            if ("datatype" in node):
                return Literal(node["value"], datatype=URIRef(node["datatype"]))
            return Literal(node["value"])

        if (node["type"] == "bnode"):
            return BNode(node["value"])

    def create_triple(self, triple: dict) -> Tuple[rdf_node, rdf_node, rdf_node]:
        return (self.create_node(triple["subject"]), self.create_node(triple["predicate"]), self.create_node(triple["object"]))
