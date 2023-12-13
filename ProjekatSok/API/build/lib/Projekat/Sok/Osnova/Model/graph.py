class Node:
    def __init__(self, id, value=None):  # Proci specifikaciju i dodati sta sve treba vrednosti, mozemo kao i vise atributa ili kao dictonary
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

    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, new_edges):
        self._edges = new_edges


class Edge:
    def __init__(self, firstNode:Node, secondNode:Node, value=None):
        self.firstNode = firstNode
        self.secondNode = secondNode
        self.value = value
        firstNode.edges.append([secondNode, value])
        #secondNode.edges.append([firstNode, value])

    def __str__(self) -> str:
        ret = ""
        ret = ret + str(self.firstNode.id) + " " + str(self.secondNode.id) + " " + str(self.value)
        return ret


class Graph:
    def __init__(self):
        self.edges = []
        self.indices = []

    def addNode(self, node:Node):
        self.indices.append([node, len(self.edges)+1])

    def addEdge(self, edge:Edge):
        self.edges.append(edge)
        self.sortEdges()
        maxIndex=float('inf')
        for index, (node, position) in enumerate(self.indices):
            if node.id==edge.firstNode.id:
                maxIndex=index
            if index>maxIndex:
                self.indices[index][1] += 1
    def getNodeById(self,id):
        for index in self.indices:
            if index[0].id == id:
                return index[0]
        return None

    def __str__(self) -> str:
        ret = "[ nodes="
        for nodes in self.indices:
            ret=ret+"["+str(nodes[0].id)+" "+str(nodes[1])+"] "
        ret=ret+"], egdes=["
        for edge in self.edges:
            ret=ret+"["+str(edge.firstNode.id)+" "+str(edge.secondNode.id)+"] "
        ret=ret+"]"
        return ret

    def sortEdges(self):
        self.edges = sorted(self.edges, key=lambda x: (x.firstNode.id, x.secondNode.id))

    def dfs(self):
        pass

    def bfs(self):
        pass

    def filter(self):
        pass
