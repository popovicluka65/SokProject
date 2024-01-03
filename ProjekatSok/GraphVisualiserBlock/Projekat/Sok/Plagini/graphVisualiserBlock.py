from Projekat.Sok.Osnova.Model.graph import Graph
from Projekat.Sok.Osnova.Services.graph import GraphVisualiserBase
from Projekat.Sok.Plagini.graphVisualiserBlockService import blockVisualize

class GraphVisualiserBlock(GraphVisualiserBase):
    def identifier(self):
        return "GrafVisualiserBlock"

    def name(self):
        return "GrafVisualiserBlock"

    def visualize(self, graph: Graph):
        block_content = blockVisualize(graph)
        with open('block.html', 'w', encoding="utf-8") as file:
            file.write(block_content)