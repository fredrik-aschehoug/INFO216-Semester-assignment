import sys
from SPARQLWrapper import SPARQLWrapper, JSON


class QueryService:

    # TODO adjust user agent; see https://w.wiki/CX6
    user_agent = "Python/%s.%s" % (sys.version_info[0], sys.version_info[1])

    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        self.sparql = SPARQLWrapper(self.endpoint_url, agent=self.user_agent)

    def execute_query(self, query):
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
