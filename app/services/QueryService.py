from aiosparql.client import SPARQLClient
from async_lru import alru_cache

from models.types import sparql_bindings


class QueryService():
    """
    Base class used for querying SPARQL endpoints.
    Uses the aiosparql SPARQLClient to support sending async requests.
    """
    user_agent = "KG-Enricher"
    headers = {'User-Agent': user_agent}

    def __init__(self, endpoint_url, triple_query):
        self.endpoint_url = endpoint_url
        self.triple_query = triple_query

    async def execute_query(self, query) -> sparql_bindings:
        client = SPARQLClient(self.endpoint_url, headers=self.headers)
        result = await client.query(query)
        await client.close()
        return result["results"]["bindings"]

    @alru_cache
    async def get_triples(self, uri: str) -> sparql_bindings:
        if (uri is None):
            return list()

        query = self.triple_query.substitute(uri=uri)
        return await self.execute_query(query)
