from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import OWL
import json
import time
from typing import Union, List, Tuple
from services.YagoService import YagoService
from services.WikidataService import WikidataService
from services.RelationService import RelationService
from models.models import Item, rdf_node
from models.namespaces import yago3, wd, p, wdt, schema, wdtn, wikibase, skos, wds
import asyncio


class GraphService:

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

    @staticmethod
    async def gather_with_concurrency(n, *tasks):
        # Run n amount of tasks concurrently
        semaphore = asyncio.Semaphore(n)

        async def sem_task(task):
            async with semaphore:
                return await task
        return await asyncio.gather(*(sem_task(task) for task in tasks))

    async def add_yago_triples(self, entity_uri):
        triples = list()
        entity_triples = await self.yagoService.get_triples(entity_uri)
        if (len(entity_triples) > 0):
            triples.append({"entity": entity_uri, "triples": entity_triples})

        for entity in triples:
            current_subject = entity["triples"][0]["subject"]
            self.yago_URIs.append((entity["entity"], current_subject["value"]))
            self.graph.add((URIRef(entity["entity"]), OWL.sameAs, self.create_node(current_subject)))
            for triple in entity["triples"]:
                self.graph.add(self.create_triple(triple))

    async def extend_yago(self) -> None:
        tasks = [self.add_yago_triples(entity) for entity in self.get_entities()]
        await asyncio.gather(*tasks)

    async def add_wd_triples(self, subject_uri):
        triples = await self.wikidataService.get_triples(subject_uri)
        for triple in triples:
            self.graph.add(self.create_triple(triple))

    async def extend_wd(self) -> None:
        wd_uris = list()
        for entity_uri, yago_uri in self.yago_URIs:
            wd_uri = await self.yagoService.get_wd_URI(yago_uri)
            self.graph.add((URIRef(entity_uri), OWL.sameAs, URIRef(wd_uri)))
            wd_uris.append(wd_uri)
        tasks = [self.add_wd_triples(uri) for uri in wd_uris]
        # Do concurrent request, but only 5 at a time
        await self.gather_with_concurrency(5, *tasks)

    async def extend(self) -> None:
        await self.extend_yago()
        await self.extend_wd()

    def annotate_relations(self):
        relationService = RelationService(self.graph)
        self.graph = relationService.get_graph()
