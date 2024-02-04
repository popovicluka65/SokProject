from typing import List, Union

from Projekat.Sok.Osnova.Model.graph import Graph as Graph, Node,Edge
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
    plugins: List[Union] = kwargs.get("graphParsers", []) + kwargs.get("graphVisualisers", []) # ovde treba da ide typing Union[GraphParserBase, GraphVisualiserBase] ali za sad ne
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
            #graf = plugin.load(kwargs["file"])
            #graf = plugin.load("example1.ttl")
            graf = plugin.load("example1.json")
            globalni_niz.append(graf)
            return graf
        if isinstance(plugin, GraphVisualiserBase):

            return plugin.visualize(globalni_niz[-1])
            #return html_string
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

def main():
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")

    consoleMenu(graphParsers=graphParsers,
                graphVisualisers=graphVisualisers,
                file="example1.json")

def django():
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    odabraniGraph = izabrana_opcija(graphParsers[0])
    write_graph_to_neo4j(URI,USERNAME,PASSWORD,odabraniGraph)
    #afterSearch = search("25","", odabraniGraph)
    #write_graph_to_neo4j(URI,USERNAME,PASSWORD,afterSearch)
    stringReprezentaicija = izabrana_opcija(graphVisualisers[0])
    return odabraniGraph,stringReprezentaicija
def write_graph_to_neo4j(uri, username, password, graph):

    db.cypher_query("MATCH (n) DETACH DELETE n")
    def create_node(tx, node):
        value_json = json.dumps(node.value)
        tx.run("CREATE (:Node {id: $id, value: $value})", id=node.id, value=value_json)

    def create_edge(tx, edge):
        tx.run("MATCH (a:Node {id: $id1}), (b:Node {id: $id2}) "
               "CREATE (a)-[:CONNECTED_TO {value: $value}]->(b)",
               id1=edge.firstNode.id, id2=edge.secondNode.id, value=edge.value)

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            for node, _ in graph.indices:
                session.write_transaction(create_node, node)

            for edge in graph.edges:
                session.write_transaction(create_edge, edge)
def retrieve_graph(tx):
    result = tx.run("MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN COLLECT(DISTINCT n) AS nodes, COLLECT(DISTINCT r) AS relationships")
    return result.data()

def search_nodes(tx, search_query, graph: Graph):
    oldGraph = graph
    newGraph = Graph()
    result = tx.run(
        """
        MATCH (n)-[r]-(m)
        WHERE any(key in keys(n) WHERE n[key] CONTAINS $search_query) AND any(key in keys(m) WHERE m[key] CONTAINS $search_query) OR any(key in keys(r) WHERE r[key] CONTAINS $search_query)
        RETURN n, r, m
        """,
        search_query=search_query
    )
    result1 = tx.run(
        """
        MATCH (n)
    WHERE any(key in keys(n) WHERE n[key] CONTAINS $search_query)
    RETURN n
        """,
        search_query=search_query
    )
    for record in result1:
        newNodeDB = record["n"]
        newNode = Node(newNodeDB.get("id"), json.loads(newNodeDB.get("value")))
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
        newNode1 = Node(node1.get("id"), json.loads(node1.get("value")))
        newNode2 = Node(node2.get("id"), json.loads(node2.get("value")))
        #print("Node1: ", newNode1, " Node2: ", newNode2, " Edge: ", newEdge, '\n')
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
def search(search_query,filter_query,graph):
    print("UDJE U SEARCH")

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with driver.session() as session:
        result = session.read_transaction(search_nodes, search_query, graph)

        return  result

    # with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
    #     with driver.session() as session:
    #         graph_data = session.read_transaction(retrieve_graph)
    #         for node in graph_data[0]['nodes']:
    #             print(node)
    #             if(searchQuery in node['id']):

        #moramo konvertovati u nas pravi graph


if __name__ == "__main__":
    main()
