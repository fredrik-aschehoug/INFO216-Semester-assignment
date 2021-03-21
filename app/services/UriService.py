from services.AsyncService import AsyncService
from config.config import settings


class UriService(AsyncService):
    def __init__(self):
        # Keys: entity, yago, wd
        self._maps = list()

    @property
    def maps(self):
        return self._maps

    @maps.setter
    def maps(self, maps):
        self._maps = maps

    def add(self, new_map):
        self._maps.append(new_map)

    def add_entities(self, entities: list):
        self._maps = [{"entity": entity} for entity in entities]

    @staticmethod
    async def extend_uri_map(map_, service, source, destination):
        """Add external URI to the uri_map"""
        map_[destination] = await service(map_[source])
        return map_

    async def add_yago_uris(self, service):
        uri_tasks = [self.extend_uri_map(uri_map, service, "entity", "yago") for uri_map in self._maps]
        self._maps = await self.gather_with_concurrency(settings.yago_endpoint_max_connections, uri_tasks)

    async def add_wd_uris(self, service):
        uri_tasks = [self.extend_uri_map(uri_map, service, "yago", "wd") for uri_map in self._maps]
        self._maps = await self.gather_with_concurrency(settings.yago_endpoint_max_connections, uri_tasks)
