from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL
import json
from services.YagoService import YagoService


def parse_input_json(raw, notation):
    g = Graph()
    data = json.dumps(raw)
    g.parse(data=data, format=notation)
    return g


def parse_input(raw, notation):
    g = Graph()
    g.parse(data=raw, format=notation)
    return g


def get_objects(g):
    qres = g.query(
        """SELECT DISTINCT ?object
       WHERE {
          ?subject ?predicate ?object .
          FILTER(!isLiteral(?object))
       }""")
    for (obj,) in qres:
        print(obj)


def get_entities(g):
    qres = g.query(
        """SELECT DISTINCT ?entity
       WHERE {
          ?subject nhterm:hasEntity ?entity .
       }""")

    entities = set([str(entity) for (entity,) in qres])
    return list(entities)


def create_node(node: dict):
    if (node["type"] == "uri"):
        return URIRef(node["value"])

    if (node["type"] == "literal"):
        if ("datatype" in node):
            return Literal(node["value"], datatype=URIRef(node["datatype"]))
        return Literal(node["value"])


def get_extended_graph(raw, notation):
    g = parse_input(raw, notation)
    yagoService = YagoService()

    g.bind("yago3", Namespace("http://yago-knowledge.org/resource/"))

    # objects = get_objects(g)
    entities = get_entities(g)
    triples = list()
    for entity in entities:
        yago_triples = yagoService.get_triples(entity)
        if (len(yago_triples) > 0):
            triples.append({"entity": entity, "triples": yago_triples})

    for entity in triples:
        g.add((URIRef(entity["entity"]), OWL.sameAs, create_node(entity["triples"][0]["subject"])))
        for triple in entity["triples"]:
            g.add((create_node(triple["subject"]), create_node(triple["predicate"]), create_node(triple["object"])))

    return g.serialize(format='turtle').decode("utf-8")
