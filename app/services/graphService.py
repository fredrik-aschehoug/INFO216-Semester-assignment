from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import OWL
import json
import time
from typing import Union, List, Tuple
from services.YagoService import YagoService
from services.WikidataService import WikidataService
from services.RelationService import RelationService
from services.UriService import UriService
from services.AsyncService import AsyncService
from models.models import Item, rdf_node
from models.namespaces import yago3, wd, p, wdt, schema, wdtn, wikibase, skos, wds
import asyncio


class GraphService(AsyncService):

    def __init__(self, params: Item):
        self.notation = params.notation
        self.graph = self.parse_input(params.graph, params.notation)
        self.graph.bind("owl", OWL)
        self.graph.bind("yago3", yago3)
        self.graph.bind("wd", wd)
        self.graph.bind("wdt", wdt)
        self.graph.bind("wdtn", wdtn)
        self.graph.bind("wikibase", wikibase)
        self.graph.bind("wds", wds)
        self.graph.bind("p", p)
        self.graph.bind("schema", schema)
        self.graph.bind("skos", skos)

        self.yagoService = YagoService()
        self.wikidataService = WikidataService()
        # Contains dictionaries used to map different URI's describing the same object
        self.uri_maps = UriService()
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
        """Return current rdflib Graph object"""
        return self.graph

    def get_graph_serialized(self, notation: str = None) -> str:
        if (notation is None):
            notation = self.notation
        return self.graph.serialize(format=notation).decode("utf-8")

    def get_entities(self) -> List[str]:
        """Run query against internal graph and return list of entity URIs"""
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

        if (node["type"] == "bnode"):
            return BNode(node["value"])

    def create_triple(self, triple: dict) -> Tuple[rdf_node, rdf_node, rdf_node]:
        return (self.create_node(triple["subject"]), self.create_node(triple["predicate"]), self.create_node(triple["object"]))

    async def add_yago_triples(self, uri) -> None:
        triples = await self.yagoService.get_triples(uri)
        if (len(triples) == 0):
            return

        subject = triples[0]["subject"]

        # Add triple: nhterm:Entity owl:sameAs yago3:Entity
        self.graph.add((URIRef(uri), OWL.sameAs, self.create_node(subject)))

        # Add triples returned from Yago3
        for triple in triples:
            self.graph.add(self.create_triple(triple))

    async def extend_yago(self) -> None:
        tasks = [self.add_yago_triples(uri_map["yago"]) for uri_map in self.uri_maps.maps]
        await self.gather(tasks)

    async def add_wd_triples(self, subject_uri) -> None:
        triples = await self.wikidataService.get_triples(subject_uri)
        for triple in triples:
            self.graph.add(self.create_triple(triple))

    async def extend_wd(self) -> None:
        for uri_map in self.uri_maps.maps:
            if (uri_map["wd"] is not None):
                self.graph.add((URIRef(uri_map["entity"]), OWL.sameAs, URIRef(uri_map["wd"])))

        # Do concurrent request, but only 5 at a time
        tasks = [self.add_wd_triples(uri_map["wd"]) for uri_map in self.uri_maps.maps]
        await self.gather_with_concurrency(5, tasks)

    async def extend(self) -> None:
        self.uri_maps.add_entities(self.get_entities())
        await self.uri_maps.add_yago_uris(self.yagoService.get_yago_URI)
        await self.uri_maps.add_wd_uris(self.yagoService.get_wd_URI)
        await self.gather([self.extend_yago(), self.extend_wd()])

    def annotate_relations(self) -> None:
        relationService = RelationService(self.graph)
        self.graph = relationService.get_graph()
