from rdflib import Graph
import json


# Open RDF file, parse, and save as serialized JSON request

SOURCE = "minimal_graph.ttl"
DESTINATION = "minimal_graph.json"
IN_NOTATION = "turtle"
OUT_NOTATION = "turtle"

g = Graph()
g.parse(SOURCE, format=IN_NOTATION)
serialized = g.serialize(format=OUT_NOTATION)

request = {
    "graph": serialized.decode(),
    "in_notation": OUT_NOTATION
}
with open(DESTINATION, 'w') as f:
    json.dump(request, f, sort_keys=True)
