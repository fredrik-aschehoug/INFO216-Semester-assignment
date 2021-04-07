from rdflib import BNode, URIRef, Literal, Graph
from rdflib.collection import Collection
from rdflib.namespace import RDF, OWL
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql.processor import SPARQLResult
from models.namespaces import nhterm
from typing import Generator


GET_ITEMS_QUERY = """
SELECT DISTINCT ?item
WHERE {
    ?item a nhterm:Item .
}
"""

GET_RELATIONS_QUERY = """
SELECT DISTINCT ?item ?entity1 ?relation ?entity2
WHERE {
    ?item nhterm:hasAnnotation ?annotation .
    ?annotation nhterm:hasEntity ?entity1 .
    ?entity1 owl:sameAs ?entity_external .
    ?entity_external ?relation ?entity_external2 .
    ?entity2 owl:sameAs ?entity_external2 .
    ?annotation2 nhterm:hasEntity ?entity2 .
    ?item nhterm:hasAnnotation ?annotation2 .
}
"""

GET_PC_RELATIONS_QUERY = """
SELECT DISTINCT ?item ?entity1 ?predicate ?entity2 ?obj
WHERE {
    ?item nhterm:hasAnnotation/nhterm:hasEntity ?entity1 .
    ?item nhterm:hasAnnotation/nhterm:hasEntity ?entity2 .
    ?entity1 owl:sameAs ?entity_external1 .
    ?entity2 owl:sameAs ?entity_external2 .

    ?entity_external1 ?predicate ?obj .
    ?entity_external2 ?predicate ?obj .

    FILTER(?entity1 != ?entity2)
}
"""


class RelationService:
    ANNOTATOR = URIRef("https://www.wikidata.org/wiki/Q106226082")

    def __init__(self, graph: Graph):
        self.graph = graph

    def _get_items(self) -> Generator[URIRef, None, None]:
        """Generator which yields all item identifiers in the graph"""

        qres = self.graph.query(GET_ITEMS_QUERY)

        for (item,) in qres:
            yield item

    def _get_relations(self, item: URIRef) -> SPARQLResult:
        """
        Get regular 1:1 relations between two entities whitin the same item.
        Return SPARQLResult in the following format: (item, entity1, relation, entity2)
        """

        query = prepareQuery(GET_RELATIONS_QUERY, initNs={"nhterm": nhterm, "owl": OWL})
        qres = self.graph.query(query, initBindings={'item': item})
        return qres

    def _get_pc_relations(self, item: URIRef) -> SPARQLResult:
        """Get entities that share a common property and object"""

        query = prepareQuery(GET_PC_RELATIONS_QUERY, initNs={"nhterm": nhterm, "owl": OWL})
        qres = self.graph.query(query, initBindings={'item': item})
        return qres

    @staticmethod
    def _get_unique_key(*args) -> hash:
        """Hash all arguments, sum the hashes, then return the hash of the sum."""
        res = 0
        for arg in args:
            res += hash(arg)
        return hash(res)

    def _prepare_pc_relations(self, relations: SPARQLResult) -> dict:
        """
        Transform the rdflib SPARQLResult object to a dictionary.
        The dictionary uses a hash of some of the variables as keys, the values are dictionaries. (See get_dict())

        Example input:
        [
            {
                item: <some GUID>,
                entity1: yago4:Paris,
                entity2: yago4:Berlin,
                predicate: rdfs:type,
                object: yago4:City
            },
            {
                item: <some GUID>,
                entity1: yago4:London,
                entity2: yago4:Oslo,
                predicate: rdfs:type,
                object: yago4:City
            }
        ]

        Produces the following dict:
        {
            <some hash>: {
                predicate: rdfs:type,
                obj: yago4:City,
                entities: {yago4:Paris, yago4:Berlin, yago4:London, yago4:Oslo},
                item: <some GUID>
            }
        }

        """
        prepared_relations = dict()

        for (item, entity1, predicate, entity2, obj) in relations:

            def get_dict() -> dict:
                return {
                    "predicate": predicate,
                    "obj": obj,
                    "entities": set(),
                    "item": item
                }

            # Use a hash of predicate, obj and item for the key. Those vaules should stay the same, while the entities may change.
            key = self._get_unique_key(predicate, obj, item)
            current_item = prepared_relations.setdefault(key, get_dict())
            current_item["entities"].update([entity1, entity2])

        return prepared_relations

    def _add_shared_pc_relations(self, relations: SPARQLResult) -> None:
        """Add the obtained predicate object relations to the graph"""
        prepared_relations = self._prepare_pc_relations(relations)

        for item in prepared_relations.values():
            relationAnnotation = BNode()
            self.graph.add((item["item"], nhterm.hasAnnotation, relationAnnotation))
            self.graph.add((relationAnnotation, RDF.type, nhterm.RelationAnnotation))
            self.graph.add((relationAnnotation, nhterm.hasAnnotator, self.ANNOTATOR))
            self.graph.add((relationAnnotation, nhterm.relationType, nhterm.sharedPredicateObjectRelation))
            self.graph.add((relationAnnotation, nhterm.predicate, item["predicate"]))
            self.graph.add((relationAnnotation, nhterm.object, item["obj"]))
            entities = BNode()
            self.graph.add((relationAnnotation, nhterm.entities, entities))
            Collection(self.graph, entities, list(item["entities"]))

    def _add_relations(self, relations: SPARQLResult) -> None:
        """Add the relations to the internal graph"""
        for (item, entity1, relation, entity2) in relations:
            relationAnnotation = BNode()
            self.graph.add((item, nhterm.hasAnnotation, relationAnnotation))
            self.graph.add((relationAnnotation, RDF.type, nhterm.RelationAnnotation))
            self.graph.add((relationAnnotation, nhterm.hasAnnotator, self.ANNOTATOR))
            self.graph.add((relationAnnotation, nhterm.relationType, nhterm.standardRelation))
            self.graph.add((relationAnnotation, nhterm.relationFrom, entity1))
            self.graph.add((relationAnnotation, nhterm.relationTo, entity2))
            self.graph.add((relationAnnotation, nhterm.hasRelation, relation))

    def annotate_relations(self) -> None:
        for item in self._get_items():
            relations = self._get_relations(item)
            self._add_relations(relations)
            shared_relations = self._get_pc_relations(item)
            self._add_shared_pc_relations(shared_relations)
