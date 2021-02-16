from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL
import json
from typing import Union, Any, List, Tuple
from services.YagoService import YagoService

rdf_node = Union[Literal, URIRef]


class GraphService:

    def __init__(self, raw: Union[str, object], notation: str):
        self.notation = notation
        self.graph = self.parse_input(raw, notation)
        self.graph.bind("yago3", Namespace("http://yago-knowledge.org/resource/"))

    @staticmethod
    def parse_input(raw: Union[str, object], notation: str) -> Graph:
        g = Graph()

        if (notation == "json-ld"):
            g.parse(data=json.dumps(raw), format=notation)
        else:
            g.parse(data=raw, format=notation)
        return g

    def get_graph(self) -> Graph:
        return self.graph

    def get_graph_serialized(self, notation: str = None) -> str:
        if (notation is None):
            notation = self.notation
        return self.graph.serialize(format=notation).decode("utf-8")

    def get_entities(self) -> List[str]:
        qres = self.graph.query(
            """SELECT DISTINCT ?entity
        WHERE {
            ?subject nhterm:hasEntity ?entity .
        }""")

        entities = set([str(entity) for (entity,) in qres])
        return list(entities)

    @staticmethod
    def create_node(node: dict) -> rdf_node:
        if (node["type"] == "uri"):
            return URIRef(node["value"])

        if (node["type"] == "literal"):
            if ("datatype" in node):
                return Literal(node["value"], datatype=URIRef(node["datatype"]))
            return Literal(node["value"])

    def create_triple(self, triple: dict) -> Tuple[rdf_node, rdf_node, rdf_node]:
        return (self.create_node(triple["subject"]), self.create_node(triple["predicate"]), self.create_node(triple["object"]))

    def extend(self, service: YagoService) -> None:
        triples = list()
        for entity in self.get_entities():
            yago_triples = service.get_triples(entity)
            if (len(yago_triples) > 0):
                triples.append({"entity": entity, "triples": yago_triples})

        for entity in triples:
            self.graph.add((URIRef(entity["entity"]), OWL.sameAs, self.create_node(entity["triples"][0]["subject"])))
            for triple in entity["triples"]:
                self.graph.add(self.create_triple(triple))


def get_objects(g):
    qres = g.query(
        """SELECT DISTINCT ?object
       WHERE {
          ?subject ?predicate ?object .
          FILTER(!isLiteral(?object))
       }""")
    for (obj,) in qres:
        print(obj)


def get_extended_graph(raw, notation):
    graphService = GraphService(raw, notation)
    yagoService = YagoService()

    graphService.extend(yagoService)

    return graphService.get_graph_serialized()
