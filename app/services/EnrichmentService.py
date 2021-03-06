from rdflib import URIRef
from rdflib.namespace import OWL

from config.config import settings
from models.models import RequestModel
from services.AsyncService import AsyncService
from services.GraphService import GraphService
from services.RelationService import RelationService
from services.UriService import UriService
from services.WikidataService import WikidataService
from services.YagoService import YagoService


class EnrichmentService(AsyncService):
    """
    Service used to orchestrate the enrichment process.
    This class should be injected as a dependency in a FastAPI route.
    """

    def __init__(self, params: RequestModel):
        # Register services
        self._graphService = GraphService(params.graph, params.in_notation, params.out_notation)
        self._yagoService = YagoService()
        self._wikidataService = WikidataService()
        self._uriService = UriService()
        self._relationService = RelationService(self._graphService.graph)

    async def _add_external_triples(self, external_uri: str, entity: str, service) -> None:
        """Get triples related to external_uri from the service and add them to the graph"""
        triples = await service.get_triples(external_uri)

        if (len(triples) == 0):
            return

        # Add triple: nhterm:Entity owl:sameAs external:Entity
        external_subject = triples[0]["subject"]
        self._graphService.add((URIRef(entity), OWL.sameAs, self._graphService.create_node(external_subject)))

        # Add triples returned from service to the graph
        for triple in triples:
            self._graphService.add(self._graphService.create_triple(triple))

    async def _extend_yago(self) -> None:
        """For each yago4 uri in the uriService, fetch related triples from yago4 endpoint and add them to the graph."""
        tasks = [self._add_external_triples(uri_map["yago"], uri_map["entity"], self._yagoService) for uri_map in self._uriService.maps]
        await self.gather_with_concurrency(settings.yago_endpoint_max_connections, tasks)

    async def _extend_wd(self) -> None:
        """For each wikidata uri in the uriService, fetch related triples from wikidata endpoint and add them to the graph."""
        tasks = [self._add_external_triples(uri_map["wd"], uri_map["entity"], self._wikidataService) for uri_map in self._uriService.maps]
        await self.gather_with_concurrency(settings.wd_endpoint_max_connections, tasks)

    async def extend(self) -> None:
        self._graphService.validate_graph()
        self._uriService.add_entities(self._graphService.get_entities())
        await self._uriService.add_yago_uris(self._yagoService.get_yago_URI)
        await self._uriService.add_wd_uris(self._yagoService.get_wd_URI)
        await self.gather([self._extend_yago(), self._extend_wd()])

    def annotate_relations(self) -> None:
        self._relationService.annotate_relations()

    def get_response(self) -> str:
        """Create the response to be returned after the enrichment."""
        return {"graph": self._graphService.get_graph_serialized(), "notation": self._graphService.notation}
