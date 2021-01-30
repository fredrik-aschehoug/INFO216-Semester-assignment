from rdflib import Graph
import json


def parse_input(raw, notation):
    g = Graph()
    data = json.dumps(raw)
    g.parse(data=data, format=notation)

    return g.serialize(format='n3').decode("utf-8")