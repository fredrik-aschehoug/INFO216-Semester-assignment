from services.QueryService import QueryService
from string import Template
import asyncio


TRIPLE_QUERY = Template("""
PREFIX wd: <http://www.wikidata.org/entity/>

SELECT DISTINCT ?predicate ?object
WHERE {
  <$uri> ?predicate ?object .
  FILTER(!isLiteral(?object) || lang(?object) = "" || langMatches(lang(?object), "en"))
}
""")


class WikidataService(QueryService):
    endpoint_url = "https://query.wikidata.org/sparql"

    def __init__(self):
        super().__init__(self.endpoint_url, TRIPLE_QUERY)
