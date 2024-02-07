from typing import List, Union
import uuid
from Projekat.Sok.Osnova.Model.graph import Graph as Graph, Node, Edge
import pkg_resources
from neo4j import GraphDatabase
import json
from neomodel import db

from Projekat.Sok.Osnova.Services.graph import (
    GraphVisualiserBase,
    GraphParserBase
)

globalni_niz = []

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"


def consoleMenu(*args, **kwargs):
    plugins: List[Union] = kwargs.get("graphParsers", []) + kwargs.get("graphVisualisers",
                                                                       [])  # ovde treba da ide typing Union[GraphParserBase, GraphVisualiserBase] ali za sad ne
    if not plugins:
        print("Nije prepoznati nijedan plugin!")
        return
    error = False
    message = None
    while True:
        print("-----------------------------------")
        if error:
            print("Pogresna vrednost uneta")
            error = False
        if message:
            print(message)
        print("Opcije: ")
        for i, plugin in enumerate(plugins):
            print(f"{i} {plugin.identifier()}")
        print(f"{len(plugins)} za izlaz")
        try:
            choice = int(input("Unesite redni broj opcije:"))
        except:
            error = True
            continue
        if choice == len(plugins):
            return
        elif 0 <= choice < len(plugins):
            poruka = izabrana_opcija(plugins[choice], **kwargs)
        else:
            error = True
    return ""


def izabrana_opcija(plugin: Union[GraphVisualiserBase, GraphParserBase], **kwargs):
    global globalni_niz
    try:
        if isinstance(plugin, GraphParserBase):
            # graf = plugin.load(kwargs["file"])
            graf = plugin.load("example1.ttl")
            # graf = plugin.load("example1.json")
            globalni_niz.append(graf)
            return graf
        if isinstance(plugin, GraphVisualiserBase):
            return plugin.visualize(globalni_niz[-1])
            # return html_string
    except Exception as e:
        print(f"Error: {e}")
    return "Radi"


def loadPlugins(pointName: str):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=pointName):
        p = ep.load()
        print(f"{ep.name} {p}")
        plugin = p()
        plugins.append(plugin)
    return plugins

def plugin_visualisators():
    graphVisualisers = loadPlugins("graph.visualiser")
    plugin_names = [type(plugin).__name__ for plugin in graphVisualisers]
    return plugin_names

def plugin_parsers():
    graphVisualisers = loadPlugins("graph.parser")
    plugin_names = [type(plugin).__name__ for plugin in graphVisualisers]
    return plugin_names

def main():
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")

    consoleMenu(graphParsers=graphParsers,
                graphVisualisers=graphVisualisers,
                file="example1.json")

def add_graph_name(graph: Graph):
    for node, position in graph.indices:
        node.graph_name = "rdf-" + str(uuid.uuid4())

def django():
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    odabraniGraph = izabrana_opcija(graphParsers[1])
    add_graph_name(odabraniGraph)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph)
    # afterSearch = search("person", "http://example.org/age", ">", 30)
    # write_graph_to_neo4j(URI, USERNAME, PASSWORD, afterSearch)
    stringReprezentaicija = izabrana_opcija(graphVisualisers[0])
    return odabraniGraph, stringReprezentaicija


def write_graph_to_neo4j(uri, username, password, graph):
    def create_node(tx, node):
        node_attributes = {}
        node_attributes["id"] = node.id
        #node_attributes["graph_name"] = node.graph_name
        for attribute in node.value:
            node_attributes[attribute] = node.value[attribute]
        tx.run("CREATE (:Node $attributes)", attributes=node_attributes)

    def create_edge(tx, edge):
        tx.run("MATCH (a:Node {id: $id1}), (b:Node {id: $id2}) "
               "CREATE (a)-[:CONNECTED_TO {value: $value}]->(b)",
               id1=edge.firstNode.id, id2=edge.secondNode.id, value=edge.value)

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            for node, _ in graph.indices:
                session.write_transaction(create_node, node)

            print(len(graph.edges))
            for edge in graph.edges:
                 session.write_transaction(create_edge, edge)


def retrieve_graph(tx):
    result = tx.run(
        "MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN COLLECT(DISTINCT n) AS nodes, COLLECT(DISTINCT r) AS relationships")
    return result.data()


def filter_nodes(tx, f_attribute, f_operator, f_value):
    newGraph = Graph()
    query = ("""
     MATCH (n)
    WHERE 
      n[$attribute] IS NOT NULL AND 
      CASE 
        WHEN $operator = '=' THEN n[$attribute] = $value 
        WHEN $operator = '!=' THEN n[$attribute] <> $value 
        WHEN $operator = '>' THEN n[$attribute] > $value 
        WHEN $operator = '<' THEN n[$attribute] < $value 
        ELSE FALSE 
      END 
    RETURN n""")
    result = tx.run(query, attribute=f_attribute, operator=f_operator, value=f_value)
    for record in result:
        newNodeDB = record["n"]
        attributes = dict(newNodeDB.items())
        id = attributes["id"]
        del attributes["id"]
        newNode = Node(id, attributes)
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode)
    # for record in result:
    #     edge = record["r"]
    #     node1 = record["n"]
    #     node2 = record["m"]
    #     newNode1 = Node(node1.get("id"), json.loads(node1.get("value")))
    #     newNode2 = Node(node2.get("id"), json.loads(node2.get("value")))
    #     # print("Node1: ", newNode1, " Node2: ", newNode2, " Edge: ", newEdge, '\n')
    #     is_node_in_graph = False
    #     for indice in newGraph.indices:
    #         node = indice[0]
    #         if node.id == newNode1.id:
    #             is_node_in_graph = True
    #             break
    #     if not is_node_in_graph:
    #         newGraph.addNode(newNode1)
    #     if edge:
    #         newEdge = Edge(newNode1, newNode2)
    #         newGraph.addEdge(newEdge)

    return newGraph


def search_nodes(tx, search_query):
    newGraph = Graph()
    result = tx.run(
        """
        MATCH (n)-[r]-(m)
        WHERE 
          ANY(key IN keys(n) WHERE toLower(n[key]) CONTAINS toLower($search_query) OR toLower(key) CONTAINS toLower($search_query)) AND
          ANY(key IN keys(m) WHERE toLower(m[key]) CONTAINS toLower($search_query) OR toLower(key) CONTAINS toLower($search_query))
        RETURN n, r, m
        """,
        search_query=search_query
    )
    result1 = tx.run(
        """
       MATCH (n)
       WHERE 
       ANY(key IN keys(n) WHERE toLower(n[key]) CONTAINS toLower($search_query) OR toLower(key) CONTAINS toLower($search_query))
       RETURN n
        """,
        search_query=search_query
    )
    for record in result1:
        newNodeDB = record["n"]
        attributes = dict(newNodeDB.items())
        id = attributes["id"]
        del attributes["id"]
        newNode = Node(id, attributes)
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode)
    for record in result:
        edge = record["r"]
        node1 = record["n"]
        node2 = record["m"]
        attributes_n = dict(node1.items())
        attributes_m = dict(node2.items())
        id_n = attributes_n["id"]
        id_m = attributes_m["id"]
        del attributes_n["id"]
        del attributes_m["id"]
        newNode1 = Node(id_n, attributes_n)
        newNode2 = Node(id_m, attributes_m)
        # print("Node1: ", newNode1, " Node2: ", newNode2, " Edge: ", newEdge, '\n')
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode1.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode1)
        if edge:
            newEdge = Edge(newNode1, newNode2)
            newGraph.addEdge(newEdge)

    return newGraph


def search(search_query, attribute, operator, value):
    print("UDJE U SEARCH")

    #zbog provere zakomentarisano
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with driver.session() as session:
        #result = session.read_transaction(filter_nodes, attribute, operator, value)
        result = session.read_transaction(search_nodes, search_query)
        return result

    # with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
    #     with driver.session() as session:
    #         graph_data = session.read_transaction(retrieve_graph)
    #         for node in graph_data[0]['nodes']:
    #             print(node)
    #             if(searchQuery in node['id']):

    # moramo konvertovati u nas pravi graph


if __name__ == "__main__":
    main()
