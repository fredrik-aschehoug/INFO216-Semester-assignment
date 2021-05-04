from rdflib import Graph
import json

# Open JSON response, parse and save in human-readable format

SOURCE = "source.json"
DESTINATION = "destination.ttl"
IN_NOTATION = "turtle"


g = Graph()

with open(SOURCE, encoding='utf-8') as json_file:
    data = json.load(json_file)
    g.parse(format=IN_NOTATION, data=data["graph"])
    g.serialize(destination=DESTINATION, format=data["notation"], encoding="utf-8")
