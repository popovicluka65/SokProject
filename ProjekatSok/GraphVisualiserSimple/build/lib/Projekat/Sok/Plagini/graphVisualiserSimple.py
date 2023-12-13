from Projekat.Sok.Osnova.Model.graph import Graph
from Projekat.Sok.Osnova.Services.graph import GraphVisualiserBase
from Projekat.Sok.Plagini.graphVisualiserSimpleService import simpleVisualize

class GraphVisualiserSimple(GraphVisualiserBase):
    def identifier(self):
        return "GrafVisualiserSimple"

    def name(self):
        return "GrafVisualiserSimple"

    def visualize(self, graph: Graph):
        simple_content=simpleVisualize(graph)
        with open('simple.html', 'w') as file:
            file.write(simple_content)