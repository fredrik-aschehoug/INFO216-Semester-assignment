from rdflib import URIRef
from rdflib.namespace import OWL
from services.GraphService import GraphService
from services.YagoService import YagoService
from services.WikidataService import WikidataService
from services.RelationService import RelationService
from services.UriService import UriService
from services.AsyncService import AsyncService
from models.models import Item
from config.config import settings


class EnrichmentService(AsyncService):

    def __init__(self, params: Item):
        # Register services
        self.graphService = GraphService(params.graph, params.notation)
        self.yagoService = YagoService()
        self.wikidataService = WikidataService()
        self.uriService = UriService()

    def get_response(self) -> str:
        return {"graph": self.graphService.get_graph_serialized(), "notation": self.graphService.notation}

    async def add_yago_triples(self, uri) -> None:
        triples = await self.yagoService.get_triples(uri)
        if (len(triples) == 0):
            return

        subject = triples[0]["subject"]

        # Add triple: nhterm:Entity owl:sameAs yago3:Entity
        self.graphService.add((URIRef(uri), OWL.sameAs, self.graphService.create_node(subject)))

        # Add triples returned from Yago3
        for triple in triples:
            self.graphService.add(self.graphService.create_triple(triple))

    async def extend_yago(self) -> None:
        tasks = [self.add_yago_triples(uri_map["yago"]) for uri_map in self.uriService.maps]
        await self.gather_with_concurrency(settings.yago_endpoint_max_connections, tasks)

    async def add_wd_triples(self, subject_uri) -> None:
        triples = await self.wikidataService.get_triples(subject_uri)
        for triple in triples:
            self.graphService.add(self.graphService.create_triple(triple))

    async def extend_wd(self) -> None:
        for uri_map in self.uriService.maps:
            if (uri_map["wd"] is not None):
                self.graphService.add((URIRef(uri_map["entity"]), OWL.sameAs, URIRef(uri_map["wd"])))

        # Do concurrent request, but only 5 at a time
        tasks = [self.add_wd_triples(uri_map["wd"]) for uri_map in self.uriService.maps]
        await self.gather_with_concurrency(settings.wd_endpoint_max_connections, tasks)

    async def extend(self) -> None:
        self.uriService.add_entities(self.graphService.get_entities())
        await self.uriService.add_yago_uris(self.yagoService.get_yago_URI)
        await self.uriService.add_wd_uris(self.yagoService.get_wd_URI)
        await self.gather([self.extend_yago(), self.extend_wd()])

    def annotate_relations(self) -> None:
        relationService = RelationService(self.graphService.graph)
        self.graphService.graph = relationService.get_graph()
