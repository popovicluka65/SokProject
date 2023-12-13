from rdflib import Graph
from API.Projekat.Sok.Osnova.Model.graph import Graph as ourGraph, Node,Edge
from rdflib import Literal
def loadGraph(filePath):
    rdfGraph = Graph()
    rdfGraph.parse(filePath, format='turtle')
    graph = ourGraph()
    for subject, predicate, obj in rdfGraph:
        #print(f"Subject: {subject}, Predicate: {predicate}, Object: {obj}")
        if graph.getNodeById(subject) is None:
            graph.addNode(Node(subject, {}))
        subjectNode = graph.getNodeById(subject)
        if isinstance(obj, Literal):
            subjectNode.value[predicate] = obj
        else:
            if graph.getNodeById(obj) is None:
                graph.addNode(Node(obj, {}))
            graph.addEdge(Edge(subjectNode, graph.getNodeById(obj), predicate))
