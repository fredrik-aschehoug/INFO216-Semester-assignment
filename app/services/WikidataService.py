from services.QueryService import QueryService
from config.config import settings
from string import Template


TRIPLE_QUERY = Template("""
PREFIX wd: <http://www.wikidata.org/entity/>

SELECT DISTINCT ?predicate ?object
WHERE {
  <$uri> ?predicate ?object .
  FILTER(!isLiteral(?object) || lang(?object) = "" || langMatches(lang(?object), "en"))
}
""")


class WikidataService(QueryService):
    def __init__(self):
        super().__init__(settings.wd_endpoint, TRIPLE_QUERY)
