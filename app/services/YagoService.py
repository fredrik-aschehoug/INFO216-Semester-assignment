from services.QueryService import QueryService
from typing import Union
from string import Template
import asyncio


base_query = Template("""
PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?predicate ?object
WHERE {
  <$uri> ?predicate ?object .
  FILTER(
    ?predicate != rdfs:label &&
    ?predicate != yago:redirectedFrom &&
    ?predicate != owl:sameAs &&
    ?predicate != skos:prefLabel &&
    ?predicate != schema:sameAs
  )
}""")

yago_uri_query = Template("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX yago3: <http://yago-knowledge.org/resource/>

SELECT ?yago_uri
WHERE {
    ?yago_uri owl:sameAs <$entity> .
    FILTER(STRSTARTS(STR(?yago_uri), STR(yago3:)))
}
LIMIT 1""")

wikidata_uri_query = Template("""
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

    async def get_triples(self, uri: str):
        def add_subject(row):
            row["subject"] = {"type": "uri", "value": uri}
            return row
        query = base_query.substitute(uri=uri)
        results = await self.execute_query(query)
        return list(map(add_subject, results))

    async def get_yago_URI(self, entity) -> Union[str, None]:
        query = yago_uri_query.substitute(entity=entity)
        results = await self.execute_query(query)
        uri = results[0].get("yago_uri", None).get("value", None) if len(results) == 1 else None
        return uri

    async def get_wd_URI(self, yago_URI) -> Union[str, None]:
        query = wikidata_uri_query.substitute(yago_URI=yago_URI)
        results = await self.execute_query(query)

        uri = results[0].get("wd_uri", None).get("value", None) if len(results) == 1 else None
        return uri
