from rdflib import Namespace, BNode
from rdflib.namespace import RDF


class RelationService:
    nhterm = Namespace("https://newshunter.uib.no/term#")

    def __init__(self, graph):
        self.graph = graph
        self.items = self.get_items()
        self.relations = self.get_relations()
        self.item_relations = self.compile_item_relations()
        self.annotate_relations()

    def get_items(self):
        qres = self.graph.query(
            """SELECT DISTINCT ?item
        WHERE {
            ?item a nhterm:Item .
        }""")
        return [str(item) for (item,) in qres]

    def get_relations(self):
        qres = self.graph.query(
            """SELECT ?item ?entity1 ?relation ?entity2
        WHERE {
            ?item a nhterm:Item .
            ?item nhterm:hasAnnotation ?annotation .
            ?annotation nhterm:hasEntity ?entity1 .
            ?entity1 owl:sameAs ?entity_external .
            ?entity_external ?relation ?entity_external2 .
            ?entity2 owl:sameAs ?entity_external2 .
        }""")

        return qres

    def get_item_relations(self, item):
        def filter_relations(relation: str):
            if str(relation[0]) == item:
                return True
            return False

        return list(filter(filter_relations, self.relations))

    def compile_item_relations(self):
        return {item: self.get_item_relations(item) for item in self.items}

    def add_relations(self, relations):
        for (item, entity1, relation, entity2) in relations:
            annotation = BNode()
            self.graph.add((annotation, RDF.type, self.nhterm.RelationAnnotation))
            self.graph.add((annotation, self.nhterm.relationFrom, entity1))
            self.graph.add((annotation, self.nhterm.relationTo, entity2))
            self.graph.add((annotation, self.nhterm.hasRelation, relation))

    def annotate_relations(self):
        for relations in self.item_relations.values():
            self.add_relations(relations)

    def get_graph(self):
        return self.graph
