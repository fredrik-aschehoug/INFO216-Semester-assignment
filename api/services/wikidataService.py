import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT DISTINCT ?item ?name WHERE {
  VALUES ?type {wd:Q5398426 wd:Q11424} ?item wdt:P31 ?type .
  ?item rdfs:label ?queryByTitle.
  OPTIONAL { ?item wdt:P1476 ?name. }
  FILTER(REGEX(?queryByTitle, "star wars", "i"))
}
LIMIT 10"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)