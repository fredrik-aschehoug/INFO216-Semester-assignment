from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL
import json
from typing import Union, List, Tuple
from services.YagoService import YagoService
from api.models import Item, rdf_node


class GraphService:

    def __init__(self, params: Item):
        self.notation = params.notation
        self.graph = self.parse_input(params.graph, params.notation)
        self.graph.bind("yago3", Namespace("http://yago-knowledge.org/resource/"))

    def __str__(self):
        return self.graph.serialize(format=self.notation).decode("utf-8")

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
            entity_triples = service.get_triples(entity)
            if (len(entity_triples) > 0):
                triples.append({"entity": entity, "triples": entity_triples})

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
