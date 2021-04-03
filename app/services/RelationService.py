from rdflib import BNode, URIRef
from rdflib.namespace import RDF, OWL
from rdflib.plugins.sparql import prepareQuery
from models.namespaces import nhterm
from typing import Generator


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
        TODO: refine query to only include external entity from same item
        Return rdflib.query.Result in the following format: (item, entity1, relation, entity2)
        """

        query = prepareQuery(
            """SELECT DISTINCT ?item ?entity1 ?relation ?entity2
        WHERE {
            ?item a nhterm:Item ;
                nhterm:hasAnnotation ?annotation .
            ?annotation nhterm:hasEntity ?entity1 .
            ?entity1 owl:sameAs ?entity_external .
            ?entity_external ?relation ?entity_external2 .
            ?entity2 owl:sameAs ?entity_external2 .
        }""", initNs={"nhterm": nhterm, "owl": OWL})
        qres = self.graph.query(query, initBindings={'item': item})
        return qres

    def _get_common_relations(self):
        """Get entities that share a common property"""

        qres = self.graph.query(
            """SELECT DISTINCT ?item ?entity1 ?relation ?entity2
        WHERE {
            ?item a nhterm:Item ;
                nhterm:hasAnnotation ?annotation .
            ?annotation nhterm:hasEntity ?entity1 .
            ?entity1 owl:sameAs ?entity_external .
            ?entity_external ?relation ?something1 .
            ?entity_external2 ?relation ?something2 .
            ?entity2 owl:sameAs ?entity_external2 .
        }""")

        return qres

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
