import sys
from aiosparql.client import SPARQLClient


class QueryService():

    # TODO adjust user agent; see https://w.wiki/CX6
    user_agent = "Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    headers = {'User-Agent': user_agent}

    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def close(self):
        self.client.close()

    async def execute_query(self, query):
        client = SPARQLClient(self.endpoint_url, headers=self.headers)
        result = await client.query(query)
        await client.close()
        return result["results"]["bindings"]
