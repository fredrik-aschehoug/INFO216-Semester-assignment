import sys
from aiosparql.client import SPARQLClient
from async_lru import alru_cache


class QueryService():

    # TODO adjust user agent; see https://w.wiki/CX6
    user_agent = "Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    headers = {'User-Agent': user_agent}

    def __init__(self, endpoint_url, triple_query):
        self.endpoint_url = endpoint_url
        self.triple_query = triple_query

    def close(self):
        self.client.close()

    async def execute_query(self, query):
        client = SPARQLClient(self.endpoint_url, headers=self.headers)
        result = await client.query(query)
        await client.close()
        return result["results"]["bindings"]

    @alru_cache
    async def get_triples(self, uri: str):
        query = self.triple_query.substitute(uri=uri)
        return await self.execute_query(query)
