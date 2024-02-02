from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
sys.path.append("..\..\ProjekatSok\Core\Projekat\Sok\Osnova")

from core_main import loadPlugins, izabrana_opcija, django
from neo4j import GraphDatabase
from django.conf import settings

# Create your views here.

def add_node(tx, node):
    print("USLO U ADD NODE")
    print(node)
    tx.run("CREATE (n:Node {id: $id, value: $value})", id=node.id, value=node.value)

# def add_edge(tx, edge):
#     tx.run("""
#         MATCH (a:Node {id: $id1}), (b:Node {id: $id2})
#         CREATE (a)-[:CONNECTED {value: $value}]->(b)
#         """, id1=edge.firstNode.id, id2=edge.secondNode.id, value=edge.value)
def write_graph_to_neo4j(graph, driver):
    # print("USAO GRAPH U FUNKCIJU")
    # print("EDGES")
    # print(graph)
    # print("INDICES")
    # with driver.session() as session:
    #     for node in graph.indices:
    #         print("NODE")
    #         print(node[0])
    #         print(type(node[0]))
    #     #    session.write_transaction(add_node, node[0])
    #     #
    #     # for edge in graph.edges:
    #     #     session.write_transaction(add_edge, edge)
    driver.close()

def index(request):
    graph, stringHTML = django()
    neo4j_settings = settings.NEO4J_DATABASES['default']
    uri = f"neo4j://{neo4j_settings['HOST']}:{neo4j_settings['PORT']}"
    print(uri)
    driver = GraphDatabase.driver(uri, auth=(neo4j_settings['USER'], neo4j_settings['PASSWORD']))
    write_graph_to_neo4j(graph, driver)
    driver.close()

    return render(request, 'proba.html', {"graph": stringHTML})
