import json
import os
from queue import Queue
from Projekat.Sok.Osnova.Model.graph import *
from Projekat.Sok.Osnova.Services.graph import GraphParserBase
from Projekat.Sok.Plagini.graphParserJSONService import loadGraph



class GraphParserJSON(GraphParserBase):
    def identifier(self):
        return "grafParserJSON"

    def name(self):
        return "grafParserJSON"

    def load(self, exampleJSON=None):
        return loadGraph(exampleJSON)