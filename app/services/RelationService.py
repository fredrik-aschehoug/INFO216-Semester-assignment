from rdflib import BNode
from rdflib.namespace import RDF
from models.namespaces import nhterm


class RelationService:

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
            """SELECT DISTINCT ?item ?entity1 ?relation ?entity2
        WHERE {
            ?item a nhterm:Item ;
                nhterm:hasAnnotation ?annotation .
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
            relationAnnotation = BNode()
            self.graph.add((item, nhterm.hasAnnotation, relationAnnotation))
            self.graph.add((relationAnnotation, RDF.type, nhterm.RelationAnnotation))
            self.graph.add((relationAnnotation, nhterm.relationFrom, entity1))
            self.graph.add((relationAnnotation, nhterm.relationTo, entity2))
            self.graph.add((relationAnnotation, nhterm.hasRelation, relation))

    def annotate_relations(self):
        for relations in self.item_relations.values():
            self.add_relations(relations)

    def get_graph(self):
        return self.graph
