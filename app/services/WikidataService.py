from string import Template

from config.config import settings
from services.QueryService import QueryService


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
    """Service used to query the wd_endpoint"""
    def __init__(self):
        super().__init__(settings.wd_endpoint, TRIPLE_QUERY)
