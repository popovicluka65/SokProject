from abc import ABC, abstractmethod
from ..Model.graph import Graph

class ServiceBase(ABC):
    @abstractmethod
    def identifier(self):
        pass

    @abstractmethod
    def name(self):
        pass

class GraphParserBase(ServiceBase):

    @abstractmethod
    def load(self):
        pass

class GraphVisualiserBase(ServiceBase): #vizualizatoru saljemo graf

    @abstractmethod
    def visualize(self, graph: Graph):
        pass