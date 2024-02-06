import datetime


class Node:
    def __init__(self, id, value=None, graph_name="NONAME"):
        self.graph_name = graph_name
        self.id = id
        self.value = value
        self.edges = []

    def __str__(self) -> str:
        ret = ""
        ret = ret + str(self.id) + " " + str(self.value)
        return ret

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def edges(self):
        return self.edges

    def parse_values(self, value):
        all_atributes = {}
        if value is None:
            self.value = value
        for key, value in value.items():
            try:
                new_value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                if isinstance(value, int):
                    new_value = int(value)
                else:
                    if isinstance(value, float):
                        new_value = float(value)
                    else:
                        if isinstance(value, str):
                            new_value = str(value)
                        else:
                            new_value = None
            all_atributes[key] = new_value
        self.value = all_atributes


class Edge:
    def __init__(self, firstNode: Node, secondNode: Node, value=None):
        self.firstNode = firstNode
        self.secondNode = secondNode
        self.value = value
        firstNode.edges.append([secondNode, value])

    def __str__(self) -> str:
        ret = ""
        ret = ret + str(self.firstNode.id) + " " + str(self.secondNode.id) + " " + str(self.value)
        return ret


class Graph:
    def __init__(self):
        self.edges = []
        self.indices = []

    def addNode(self, node: Node):
        self.indices.append([node, len(self.edges) + 1])

    def addEdge(self, edge: Edge):
        self.edges.append(edge)
        self.sortEdges()
        maxIndex = float('inf')
        for index, (node, position) in enumerate(self.indices):
            if node.id == edge.firstNode.id:
                maxIndex = index
            if index > maxIndex:
                self.indices[index][1] += 1

    def __str__(self) -> str:
        ret = "[ nodes="
        for nodes in self.indices:
            ret = ret + "[" + str(nodes[0].id) + " " + str(nodes[1]) + " ] "
        ret = ret + "], egdes=["
        for edge in self.edges:
            ret = ret + "[" + str(edge.firstNode.id) + " " + str(edge.secondNode.id) + "] "
        ret = ret + "]"
        return ret

    def sortEdges(self):
        self.edges = sorted(self.edges, key=lambda x: (x.firstNode.id, x.secondNode.id))

    def dfs(self):
        pass

    def bfs(self):
        pass

    def filter(self):
        pass

    def indices(self):
        return self.indices

    def __len__(self):
        return len(self.indices)

    def parse_nodes(self):
        for node, position in self.indices:
            node.parse_values(node.value)

    def getNodeById(self,id):
        for index in self.indices:
            if index[0].id == id:
                return index[0]
        return None
