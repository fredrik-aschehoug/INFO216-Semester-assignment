from services.QueryService import QueryService
from typing import Union
from string import Template
import asyncio


base_query = Template("""
PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>

SELECT ?subject ?predicate ?object
WHERE {
  ?subject owl:sameAs <$entity> .
  ?subject ?predicate ?object .
  FILTER(
    ?predicate != rdfs:label &&
    ?predicate != yago:redirectedFrom &&
    ?predicate != owl:sameAs &&
    ?predicate != skos:prefLabel &&
    ?predicate != schema:sameAs
  )
}""")

wikidata_query = Template("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX wd: <http://www.wikidata.org/entity/>

SELECT ?wd_uri
WHERE {
    <$yago_URI> owl:sameAs ?wd_uri .
    FILTER(STRSTARTS(STR(?wd_uri), STR(wd:)))
}
LIMIT 1""")


class YagoService(QueryService):

    # endpoint_url = "https://imdb.uib.no/bg-yago3/namespace/yago3/sparql"
    endpoint_url = "https://yago-knowledge.org/sparql/query"

    def __init__(self):
        super().__init__(self.endpoint_url)

    async def get_triples(self, entity: str):
        query = base_query.substitute(entity=entity)
        results = self.execute_query(query)
        return results

    def get_wd_URI(self, yago_URI) -> Union[str, None]:
        query = wikidata_query.substitute(yago_URI=yago_URI)
        results = self.execute_query(query)

        uri = (None, results[0].get("wd_uri", None).get("value", None))[len(results) == 1]
        return uri
