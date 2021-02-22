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

wikidata_query = """prefix owl: <http://www.w3.org/2002/07/owl#>
PREFIX wd: <http://www.wikidata.org/entity/>


SELECT ?uri
WHERE {
	yago3:Belgium owl:sameAs ?uri .
  FILTER(STRSTARTS(STR(?uri), STR(wd:)))
}
LIMIT 10"""


class YagoService(QueryService):

    # endpoint_url = "https://imdb.uib.no/bg-yago3/namespace/yago3/sparql"
    endpoint_url = "https://yago-knowledge.org/sparql/query"

    def __init__(self):
        super().__init__(self.endpoint_url)

    @staticmethod
    def build_query(entity: str):
        return base_query.replace("<entity>", entity)

    def get_triples(self, entity: str):
        query = self.build_query(entity)
        results = self.execute_query(query)
        return results

    def get_wikidata_URI(self):
        query = wikidata_query.replace("<entity>", entity)
        
