from queue import Queue
import json
from abc import ABC, abstractmethod
from Projekat.Sok.Osnova.Model.graph import *
import os

def get_absolute_path(file_path):
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "file", file_path)

def load_config():
    file=get_absolute_path('config.json')
    with open(file) as config_file:
        config = json.load(config_file)
    return config['connection']

connection = load_config()

class GraphHandler(ABC):
    @abstractmethod
    def parseNodes(self,g, obj):
        pass

    @abstractmethod
    def parseEdges(self,g:Graph):
        pass

    def findNodeByRef(self,g,atr):
        nodes=[]
        for node, position in g.indices:
            if node.value is not None:
                dict=node.value
                for key,value in dict.items():
                    if value==atr:
                        nodes.append(node.value)
                        return nodes
        return nodes

    def findNodeByDict(self,g,nodeDict):
        for node,possition in g.indices:
            if node.value==nodeDict:
                return node

class CyklicGraph(GraphHandler):
    def parseNodes(self,g, obj):
        visited=[]
        q=Queue()
        q.put(obj)
        visited.append(obj)
        while not q.empty():
            current=q.get()
            node_id = len(g)+1
            new_node=Node(node_id)
            g.addNode(new_node)
            edges=[]
            attributes={}
            for key,values in current.items():
                if isinstance(values, (list, dict)):
                    for neighbor in values:
                        edges.append(neighbor)
                        if neighbor not in visited:
                            q.put(neighbor)
                            visited.append(neighbor)
                else:
                    attributes[key]=values
                if connection in key:
                    attribute=current[connection]
                    nodes=self.findNodeByRef(g,attribute)
                    if nodes!=[]:
                        for node in nodes:
                            edges.append(node)
            new_node.edges=edges
            new_node.value=attributes
    def parseEdges(self,g):
        for node, position in g.indices:
            if node.edges != []:
                new_att = {}
                for att in node.value:
                    if att != connection:
                        new_att[att] = node.value[att]
                node.value = new_att
                for nodeE in node.edges:
                    nodeFull=self.findNodeByDict(g,nodeE)
                    if nodeFull is None:
                        if connection in nodeE:
                            del nodeE[connection]
                            nodeFull = self.findNodeByDict(g, nodeE)
                            if nodeFull is not None:
                                e=Edge(node,nodeFull)
                                g.addEdge(e)
                    else:
                        e = Edge(node, nodeFull)
                        g.addEdge(e)

class AcyklicGraph(GraphHandler):
    def parseNodes(self,g, obj):
        visited=[]
        q=Queue()
        q.put(obj)
        visited.append(obj)
        node_id = len(g)+1
        while not q.empty():
            current=q.get()
            node_id = len(g)+1
            new_node=Node(node_id)
            g.addNode(new_node)
            edges=[]
            attributes={}
            for key,values in current.items():
                if isinstance(values, (list, dict)):
                    for neighbor in values:
                        edges.append(neighbor)
                        if neighbor not in visited:
                            q.put(neighbor)
                            visited.append(neighbor)
                else:
                    attributes[key]=values
            new_node.edges=edges
            new_node.value=attributes

    def parseEdges(self,g):
        for node,position in g.indices:
            if node.edges!=[]:
                for nodeE in node.edges:
                    nodeFull=self.findNodeByDict(g,nodeE)
                    if nodeFull is not None:
                        e=Edge(node,nodeFull)
                        g.addEdge(e)

class LoadGraph:
    def __init__(self,obj):
        if not self.has_cycle(obj):
            self.graphParser: GraphHandler = AcyklicGraph()
        else:
            self.graphParser: GraphHandler = CyklicGraph()

    @property
    def graphParser(self):
        return self._graphParser

    @graphParser.setter
    def graphParser(self, new_graphParser: GraphHandler):
        self._graphParser = new_graphParser

    def load_graph(self, g,obj):
        self.graphParser.parseNodes(g,obj)
        self.graphParser.parseEdges(g)
        print(g)

    def has_cycle(self,obj):
        if connection in json.dumps(obj):
            return True
        return False

def loadGraph(fileJSON):
    absolute_path=get_absolute_path(fileJSON)
    with open(absolute_path, 'r') as file:
        obj2 = json.load(file)
    graph=Graph()
    g = LoadGraph(obj2)
    g.load_graph(graph,obj2)
    print(graph)
    return graph
