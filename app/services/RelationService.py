from rdflib import BNode, URIRef, Literal
from rdflib.collection import Collection
from rdflib.namespace import RDF, OWL
from rdflib.plugins.sparql import prepareQuery
from models.namespaces import nhterm
from typing import Generator
import json
from operator import itemgetter
from services.GraphService import GraphService

class RelationService:
    ANNOTATOR = URIRef("https://www.wikidata.org/wiki/Q106226082")

    def __init__(self, graph):
        self.graph = graph

    def _get_items(self) -> Generator[URIRef, None, None]:
        """Generator which yields all item identifiers in the graph"""

        qres = self.graph.query(
            """SELECT DISTINCT ?item
        WHERE {
            ?item a nhterm:Item .
        }""")

        for (item,) in qres:
            yield item

    def _get_relations(self, item):
        """
        Get regular 1:1 relations between two entities whitin the same item.
        Return rdflib.query.Result in the following format: (item, entity1, relation, entity2)
        """

        query = prepareQuery(
            """SELECT DISTINCT ?item ?entity1 ?relation ?entity2
        WHERE {
            ?item nhterm:hasAnnotation ?annotation .
            ?annotation nhterm:hasEntity ?entity1 .
            ?entity1 owl:sameAs ?entity_external .
            ?entity_external ?relation ?entity_external2 .
            ?entity2 owl:sameAs ?entity_external2 .
            ?annotation2 nhterm:hasEntity ?entity2 .
            ?item nhterm:hasAnnotation ?annotation2 .
        }""", initNs={"nhterm": nhterm, "owl": OWL})
        qres = self.graph.query(query, initBindings={'item': item})
        return qres

    def _get_shared_relations(self, item):
        """Get entities that share a common property and object"""

        query = prepareQuery(
            """SELECT DISTINCT ?item ?entity1 ?relation ?entity2 ?obj
        WHERE {
            ?item nhterm:hasAnnotation/nhterm:hasEntity ?entity1 .
            ?item nhterm:hasAnnotation/nhterm:hasEntity ?entity2 .
            ?entity1 owl:sameAs ?entity_external1 .
            ?entity2 owl:sameAs ?entity_external2 .

            ?entity_external1 ?relation ?obj .
            ?entity_external2 ?relation ?obj .

            FILTER(?entity1 != ?entity2)
        }""", initNs={"nhterm": nhterm, "owl": OWL})
        qres = self.graph.query(query, initBindings={'item': item})
        return qres

    @staticmethod
    def _prepare_relations(relations):
        prepared_relations = dict()

        # results = json.loads(relations.serialize(format="json"))["results"]["bindings"]

        # for row in results:
        #     item, entity1, relation, entity2, obj = itemgetter('item', 'entity1', 'relation', 'entity2', 'obj')(row)
        #     key = "{}{}".format(relation["value"], obj["value"])
        #     print("key:", key)
        #     current_item = prepared_relations.get(key, None)
        #     if (current_item is not None):
        #         # print("appending......")
        #         current_item["entities"].add(GraphService.create_node(entity1))
        #         current_item["entities"].add(GraphService.create_node(entity2))
        #     else:
        #         # print("inserting.....")
        #         prepared_relations[key] = {
        #             "predicate": GraphService.create_node(relation),
        #             "obj": GraphService.create_node(obj),
        #             "entities": set([GraphService.create_node(entity1), GraphService.create_node(entity2)]),
        #             "item": GraphService.create_node(item)
        #         }
        for (item, entity1, relation, entity2, obj) in relations:
            key = "{}{}".format(relation, obj)
            # print("key:", key)
            current_item = prepared_relations.get(key, None)
            if (current_item is not None):
                # print("appending......")
                current_item["entities"].add(entity1)
                current_item["entities"].add(entity2)
            else:
                # print("inserting.....")
                prepared_relations[key] = {
                    "predicate": relation,
                    "obj": obj,
                    "entities": set([entity1, entity2]),
                    "item": item
                }
            # print("loop end")
        return prepared_relations

    # 141 secs
    def _add_shared_relations(self, relations):
        prepared_relations = self._prepare_relations(relations)
        # Add relations to graph.
        for item in prepared_relations.values():
            relationAnnotation = BNode()
            self.graph.add((item["item"], nhterm.hasAnnotation, relationAnnotation))
            self.graph.add((relationAnnotation, RDF.type, nhterm.RelationAnnotation))
            self.graph.add((relationAnnotation, nhterm.hasAnnotator, self.ANNOTATOR))
            self.graph.add((relationAnnotation, nhterm.relationType, Literal("Shared predicate and object")))
            self.graph.add((relationAnnotation, nhterm.predicate, item["predicate"]))
            self.graph.add((relationAnnotation, nhterm.object, item["obj"]))
            entities = BNode()
            self.graph.add((relationAnnotation, nhterm.entities, entities))
            Collection(self.graph, entities, list(item["entities"]))

    def _add_relations(self, relations):
        """Add the relations to the internal graph"""
        for (item, entity1, relation, entity2) in relations:
            relationAnnotation = BNode()
            self.graph.add((item, nhterm.hasAnnotation, relationAnnotation))
            self.graph.add((relationAnnotation, RDF.type, nhterm.RelationAnnotation))
            self.graph.add((relationAnnotation, nhterm.hasAnnotator, self.ANNOTATOR))
            self.graph.add((relationAnnotation, nhterm.relationFrom, entity1))
            self.graph.add((relationAnnotation, nhterm.relationTo, entity2))
            self.graph.add((relationAnnotation, nhterm.hasRelation, relation))

    def annotate_relations(self):
        for item in self._get_items():
            relations = self._get_relations(item)
            self._add_relations(relations)
            shared_relations = self._get_shared_relations(item)
            self._add_shared_relations(shared_relations)
