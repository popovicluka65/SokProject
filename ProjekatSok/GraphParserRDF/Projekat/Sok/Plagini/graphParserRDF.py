from Projekat.Sok.Osnova.Services.graph import GraphParserBase
from Projekat.Sok.Plagini.graphParserRDFService import loadGraph

class GraphParserRDF(GraphParserBase):
    def identifier(self):
        return "GrafParserRDF"
    def name(self):
        return "grafParserJSON"

    def load(self, example_rdf_path=None):
        return loadGraph(example_rdf_path)