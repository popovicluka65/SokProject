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
    plugins: List[Union] = kwargs.get("graphParsers", []) + kwargs.get("graphVisualisers",[])  # ovde treba da ide typing Union[GraphParserBase, GraphVisualiserBase] ali za sad ne
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
            #graf = plugin.load("example1.ttl")
            graf = plugin.load("example1.json")
            globalni_niz.append(graf)
            return graf
        if isinstance(plugin, GraphVisualiserBase):
            return plugin.visualize(globalni_niz[-1])
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
    graph_name=""+str(uuid.uuid4())
    for node, position in graph.indices:
        node.graph_name =graph_name

def django():
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    delete_all_graphs()
    odabraniGraph = izabrana_opcija(graphParsers[0])
    odabraniGraph1 = izabrana_opcija(graphParsers[0])
    add_graph_name(odabraniGraph)
    add_graph_name(odabraniGraph1)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph1)
    graph_filtered = search("Person", "http://example.org/age", ">", 30, odabraniGraph.indices[0][0].graph_name)
    stringReprezentaicija = izabrana_opcija(graphVisualisers[1])
    return graph_filtered, stringReprezentaicija

def delete_all_graphs():
    db.cypher_query("MATCH (n) DETACH DELETE n")

def delete_graph(graph_name):
    query = "MATCH (n {graph_name: $graphName}) DETACH DELETE n"
    params = {"graphName": graph_name}
    db.cypher_query(query, params)

def get_edges(graph_name):
    query = """
        MATCH (n)-[r]->(m)
        WHERE n.graph_name = $graph_name AND m.graph_name = $graph_name
        RETURN n, r, m
    """
    params = {"graph_name": graph_name}
    return db.cypher_query(query, params)

def get_unique_graph_names():
    query = "MATCH (n) WHERE n.graph_name IS NOT NULL RETURN DISTINCT n.graph_name AS UniqueGraphNames"
    results, _ = db.cypher_query(query)
    if results:
        unique_graph_names = [record[0] for record in results]
        return unique_graph_names
    else:
        return []


def write_graph_to_neo4j(uri, username, password, graph):
    def create_node(tx, node):
        node_attributes = {}
        node_attributes["id"] = node.id
        node_attributes["graph_name"] = node.graph_name
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


def filter_nodes(tx, f_attribute, f_operator, f_value, graph_name):     #fali query za grane
    newGraph = Graph()
    query = ("""
     MATCH (n)
    WHERE
      (n.graph_name = $graph_name) AND
      (n[$attribute] IS NOT NULL) AND 
      CASE 
        WHEN $operator = '=' THEN n[$attribute] = $value 
        WHEN $operator = '!=' THEN n[$attribute] <> $value 
        WHEN $operator = '>' THEN n[$attribute] > $value 
        WHEN $operator = '<' THEN n[$attribute] < $value 
        ELSE FALSE 
      END 
    RETURN n""")
    result = tx.run(query, attribute=f_attribute, operator=f_operator, value=f_value, graph_name=graph_name)
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

def findNodeByDict(g,nodeDict):
        for node,possition in g.indices:
            if node.value==nodeDict:
                return node

def search_nodes(tx, search_query, graph_name):         #ne brisu se grane nesto
    newGraph = Graph()
    result = tx.run(
        """
        MATCH (n)-[r]-(m)
        WHERE
          (n.graph_name = $graph_name AND m.graph_name = $graph_name) AND
          ANY(key IN keys(n) WHERE n[key] CONTAINS $search_query OR key CONTAINS $search_query) AND
          ANY(key IN keys(m) WHERE m[key] CONTAINS $search_query OR key CONTAINS $search_query)
        RETURN n, r, m
        """,
        search_query=search_query,
        graph_name=graph_name
    )
    result1 = tx.run(
        """
       MATCH (n)
       WHERE
       n.graph_name = $graph_name AND
       ANY(key IN keys(n) WHERE n[key] CONTAINS $search_query AND key CONTAINS $search_query)
       RETURN n
        """,
        search_query=search_query,
        graph_name=graph_name
    )
    for record in result1:
        newNodeDB = record["n"]
        attributes = dict(newNodeDB.items())
        id = attributes["id"]
        del attributes["id"]
        attributes["graph_name"]=graph_name
        newNode = Node(id, attributes,graph_name)
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
    #     attributes_n = dict(node1.items())
    #     attributes_m = dict(node2.items())
    #     id_n = attributes_n["id"]
    #     id_m = attributes_m["id"]
    #     del attributes_n["id"]
    #     del attributes_m["id"]
    #     newNode1 = Node(id_n, attributes_n,graph_name)
    #     newNode2 = Node(id_m, attributes_m,graph_name)
    #     is_node_in_graph = False
    #     for indice in newGraph.indices:
    #         node = indice[0]
    #         if node.id == newNode1.id:
    #             is_node_in_graph = True
    #             break
    #     if not is_node_in_graph:
    #         newGraph.addNode(newNode1)
    #     if edge:
    #          newEdge = Edge(newNode1, newNode2)
    #          newNode1.edges.append(newNode2)
    #          #newGraph.addEdge(newEdge)
    # for node, position in newGraph.indices:
    #     if node.edges != []:
    #         new_att = {}
    #         node.value = new_att
    #         for nodeE in node.edges:
    #             nodeFull = findNodeByDict(newGraph, nodeE)
    #             e = Edge(node, nodeFull)
    #             newGraph.addEdge(e)
    return newGraph


def search(search_query, attribute, operator, value, graph_name):

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with driver.session() as session:
        if(search_query!=""):
            resultSearch = session.read_transaction(search_nodes, search_query, graph_name)
            delete_graph(graph_name)
            write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultSearch)
        resultFilter = session.read_transaction(filter_nodes, attribute, operator, value, graph_name)
        delete_graph(graph_name)
        write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultFilter)
        print("POSLE SEARCHA i Filtera")
        print(resultFilter)
        return resultFilter


if __name__ == "__main__":
    main()
