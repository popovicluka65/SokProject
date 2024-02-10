from rdflib import Graph, URIRef
from Projekat.Sok.Osnova.Model.graph import Graph as ourGraph, Node,Edge
from rdflib import Literal, XSD
import os

def get_absolute_path(file_path):
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "..","..", "file", file_path)
def convertValue(obj):
    if obj.datatype == URIRef(str(XSD.integer)):
        return int(obj)
    elif obj.datatype == URIRef(str(XSD.float)):
        return float(obj)
    elif obj.datatype == URIRef(str(XSD.double)):
        return float(obj)
    elif obj.datatype == URIRef(str(XSD.boolean)):
        return bool(obj)
    elif obj.language:
        return str(obj)
    else:
        return obj.value
def loadGraph(filePath):
    rdfGraph = Graph()
    rdfGraph.parse(get_absolute_path(filePath), format='turtle')
    graph = ourGraph()
    for subject, predicate, obj in rdfGraph:
        #print(f"Subject: {subject}, Predicate: {predicate}, Object: {obj}")
        if graph.getNodeById(subject) is None:
            graph.addNode(Node(subject, {}))
        subjectNode = graph.getNodeById(subject)
        if isinstance(obj, Literal):
            subjectNode.value[predicate] = convertValue(obj)
        else:
            if graph.getNodeById(obj) is None:
                graph.addNode(Node(obj, {}))
            graph.addEdge(Edge(subjectNode, graph.getNodeById(obj), predicate))
    return graph