from services.QueryService import QueryService

base_query = """PREFIX yago: <http://yago-knowledge.org/resource/>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?subject ?predicate ?object
WHERE {
  ?subject owl:sameAs <<entity>> .
  ?subject ?predicate ?object .
  FILTER(
    ?predicate != rdfs:label &&
    ?predicate != yago:redirectedFrom &&
    ?predicate != owl:sameAs &&
    ?predicate != skos:prefLabel
  )
}"""


class YagoService(QueryService):

    endpoint_url = "https://imdb.uib.no/bg-yago3/namespace/yago3/sparql"

    def __init__(self):
        super().__init__(self.endpoint_url)

    @staticmethod
    def build_query(entity: str):
        return base_query.replace("<entity>", entity)

    def get_triples(self, entity: str):
        # print("Entity: %s" % entity)
        query = self.build_query(entity)
        results = self.execute_query(query)
        return results
