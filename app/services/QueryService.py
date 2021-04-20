from aiosparql.client import SPARQLClient
from typing import Union

from models.types import sparql_bindings


class QueryService():
    """
    Base class used for querying SPARQL endpoints.
    Uses the aiosparql SPARQLClient to support sending async requests.
    """
    _user_agent = "KG-Enricher"
    _headers = {'User-Agent': _user_agent}

    def __init__(self, endpoint_url, triple_query):
        self._endpoint_url = endpoint_url
        self._triple_query = triple_query

    async def execute_query(self, query) -> sparql_bindings:
        """Instantiate a SPARQLClient, run the provided query, close the client, then return the bindings."""
        client = SPARQLClient(self._endpoint_url, headers=self._headers)
        result = await client.query(query)
        await client.close()
        return result["results"]["bindings"]

    async def get_triples(self, uri: Union[str, None]) -> sparql_bindings:
        """Prepares the triple_query with the provided uri, executes it and returns the result."""
        if (uri is None):
            return list()

        query = self._triple_query.substitute(uri=uri)
        return await self.execute_query(query)
