from typing import Callable, Generator, List, Union

from config.config import settings
from models.types import uri_map, uri_maps
from services.AsyncService import AsyncService


class UriService(AsyncService):
    """
    Service to keep track of the entities and their equivalent URIs in different namespaces.

    If we assume that the following statement is true:
    dbpedia:Belgium a nhterm:Entity ;
        owl:sameAs wd:Q31, yago3:Belgium .

    We want to store this information in this service, in a dictionary:
    {
        entity: "http://dbpedia.org/resource/Belgium",
        yago: "http://yago-knowledge.org/resource/Belgium",
        wd: "http://www.wikidata.org/entity/Belgium"
    }

    This dictionary will then be stored in a list (self._maps) which contains a dictionary for each entity in the graph.
    """
    def __init__(self):
        self._maps = list()

    @property
    def maps(self) -> uri_maps:
        """List of dicts with keys: entity, yago, wd. Each value is a URI string"""
        return self._maps

    def add_entities(self, entities: Generator[str, None, None]) -> None:
        """Add entities to the internal list of maps"""
        self._maps = [{"entity": entity} for entity in entities]

    @staticmethod
    async def _extend_uri_map(map_: uri_map, service: Callable[[str], Union[str, None]], source, destination) -> uri_map:
        """Add external URI to the uri_map in the parameter"""
        map_[destination] = await service(map_[source])
        return map_

    async def add_yago_uris(self, service: Callable[[str], Union[str, None]]) -> None:
        """Add yago to the internal list of maps"""
        uri_tasks = [self._extend_uri_map(uri_map, service, "entity", "yago") for uri_map in self._maps]
        self._maps = await self.gather_with_concurrency(settings.yago_endpoint_max_connections, uri_tasks)

    async def add_wd_uris(self, service: Callable[[str], Union[str, None]]) -> None:
        """Add wd to the internal list of maps"""
        uri_tasks = [self._extend_uri_map(uri_map, service, "yago", "wd") for uri_map in self._maps]
        self._maps = await self.gather_with_concurrency(settings.yago_endpoint_max_connections, uri_tasks)
