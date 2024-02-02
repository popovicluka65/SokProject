from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
sys.path.append("..\..\ProjekatSok\Core\Projekat\Sok\Osnova")
from neomodel import db
from core_main import loadPlugins, izabrana_opcija, django
from neo4j import GraphDatabase
from django.conf import settings
from .models import *

def write_graph_to_neo4j(graph):
    db.cypher_query("MATCH (n) DETACH DELETE n")
    for node in graph.indices:
        node_database=NodeData(node[0].id,node[0].value)
        print(node_database)
        node_database.save()

def index(request):
    graph, stringHTML = django()
    write_graph_to_neo4j(graph)

    return render(request, 'proba.html', {"graph": stringHTML})
