from rdflib import Graph, URIRef, Literal
from rdflib.namespace import OWL
import json
from typing import Union, List, Tuple
from services.YagoService import YagoService
from services.RelationService import RelationService
from api.models import Item, rdf_node
from api.namespaces import yago3


class GraphService:

    def __init__(self, params: Item):
        self.notation = params.notation
        self.graph = self.parse_input(params.graph, params.notation)
        self.graph.bind("yago3", yago3)
        self.graph.bind("owl", OWL)

        self.yagoService = YagoService()
        self.yago_URIs = list()
        self.wd_URIs = list()

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

    def extend_yago(self) -> None:
        triples = list()
        for entity in self.get_entities():
            entity_triples = self.yagoService.get_triples(entity)
            if (len(entity_triples) > 0):
                triples.append({"entity": entity, "triples": entity_triples})

        for entity in triples:
            current_subject = entity["triples"][0]["subject"]
            self.yago_URIs.append(current_subject["value"])
            self.graph.add((URIRef(entity["entity"]), OWL.sameAs, self.create_node(current_subject)))
            for triple in entity["triples"]:
                self.graph.add(self.create_triple(triple))

    def extend_wd(self) -> None:
        for uri in self.yago_URIs:
            wd_uri = self.yagoService.get_wd_URI(uri)

    def extend(self) -> None:
        self.extend_yago()
        self.extend_wd()

    def annotate_relations(self):
        relationService = RelationService(self.graph)
        self.graph = relationService.get_graph()
