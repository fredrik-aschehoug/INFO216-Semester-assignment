from services.QueryService import QueryService
from string import Template
import asyncio


base_query = Template("""
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
        super().__init__(self.endpoint_url)

    async def get_triples(self, uri: str):
        def add_subject(row):
            row["subject"] = {"type": "uri", "value": uri}
            return row
        query = base_query.substitute(uri=uri)
        results = await self.execute_query(query)
        return map(add_subject, results)
