from async_lru import alru_cache
from string import Template
from typing import Union

from config.config import settings
from services.QueryService import QueryService


TRIPLE_QUERY = Template("""
PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>

SELECT DISTINCT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
  FILTER(
    ?predicate != yago:redirectedFrom &&
    ?predicate != owl:sameAs &&
    ?predicate != skos:prefLabel &&
    ?predicate != schema:sameAs
  )
  FILTER(!isLiteral(?object) || lang(?object) = "" || langMatches(lang(?object), "en"))
  BIND(<$uri> AS ?subject)
}""")

YAGO_URI_QUERY = Template("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX yago4: <http://yago-knowledge.org/resource/>

SELECT ?yago_uri
WHERE {
    ?yago_uri owl:sameAs <$entity> .
    FILTER(STRSTARTS(STR(?yago_uri), STR(yago4:)))
}
LIMIT 1""")

WIKIDATA_URI_QUERY = Template("""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX wd: <http://www.wikidata.org/entity/>

SELECT ?wd_uri
WHERE {
    <$yago_URI> owl:sameAs ?wd_uri .
    FILTER(STRSTARTS(STR(?wd_uri), STR(wd:)))
}
LIMIT 1""")


class YagoService(QueryService):
    """Service used to query the yago_endpoint"""
    def __init__(self):
        super().__init__(settings.yago_endpoint, TRIPLE_QUERY)

    @alru_cache
    async def _get_external_URI(self, query: str, result_name: str) -> Union[str, None]:
        """
        Query the SPARQL endpoint with the supplied query.
        From the query result, take the first row and return the variable named result_name if it exists.
        """
        results = await self.execute_query(query)

        # Check if URI exist in the results object, default to None
        result = results[0].get(result_name, None) if len(results) == 1 else None
        uri = result.get("value", None) if result is not None else None
        return uri

    async def get_yago_URI(self, entity: str) -> Union[str, None]:
        """Given a nhterm:Entity, fetch the corresponding yago uri and return it if it exists."""
        query = YAGO_URI_QUERY.substitute(entity=entity)
        return await self._get_external_URI(query, "yago_uri")

    async def get_wd_URI(self, yago_URI: str) -> Union[str, None]:
        """Given a yago uri, fetch the corresponding wikidata uri and return it if it exists."""
        query = WIKIDATA_URI_QUERY.substitute(yago_URI=yago_URI)
        return await self._get_external_URI(query, "wd_uri")
