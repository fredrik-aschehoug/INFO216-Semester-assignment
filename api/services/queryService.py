import sys
from SPARQLWrapper import SPARQLWrapper, JSON, N3, RDFXML


class QueryService:

    @staticmethod
    def execute_query(endpoint_url, query):
        user_agent = "Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results["results"]["bindings"]
