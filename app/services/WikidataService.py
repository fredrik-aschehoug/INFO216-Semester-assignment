from services.QueryService import QueryService
from config.config import settings
from string import Template


TRIPLE_QUERY = Template("""
PREFIX wd: <http://www.wikidata.org/entity/>

SELECT DISTINCT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
  FILTER(!isLiteral(?object) || lang(?object) = "" || langMatches(lang(?object), "en"))
  BIND(<$uri> AS ?subject)
}
""")


class WikidataService(QueryService):
    def __init__(self):
        super().__init__(settings.wd_endpoint, TRIPLE_QUERY)
