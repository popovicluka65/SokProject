from datetime import datetime
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
            if (type(plugin).__name__ == "GraphParserRDF"):
                graf = plugin.load("example1.ttl")
            else:
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

def initialization(parser,visualiser):
    delete_all_graphs()
    odabraniGraph, stringReprezentaicija = add_workspace(parser, visualiser)
    return odabraniGraph, stringReprezentaicija

def add_workspace(parser,visualiser):
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    odabraniGraph = izabrana_opcija(graphParsers[parser])

    add_graph_name(odabraniGraph)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph)
    html = izabrana_opcija(graphVisualisers[visualiser])
    return odabraniGraph, html

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
        tx.run(
            "MATCH (a:Node {id: $id1, graph_name: $graph_name1}), (b:Node {id: $id2, graph_name: $graph_name2}) "
            "WHERE $graph_name1 = $graph_name2 "
            "CREATE (a)-[:CONNECTED_TO {value: $value}]->(b)",
            id1=edge.firstNode.id,
            id2=edge.secondNode.id,
            value=edge.value,
            graph_name1=edge.firstNode.graph_name,
            graph_name2=edge.secondNode.graph_name
        )
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        with driver.session() as session:
            for node, _ in graph.indices:
                session.write_transaction(create_node, node)

            #print(len(graph.edges))
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
    query1 = ("""
        MATCH (n)-[r]-(m)
        WHERE
          (n.graph_name = $graph_name) AND
          (n[$attribute] IS NOT NULL) AND 
          CASE 
            WHEN $operator = '=' THEN n[$attribute] = $value  AND m[$attribute] = $value
            WHEN $operator = '!=' THEN n[$attribute] <> $value AND m[$attribute] <> $value
            WHEN $operator = '>' THEN n[$attribute] > $value AND m[$attribute]  > $value
            WHEN $operator = '<' THEN n[$attribute] < $value AND m[$attribute] < $value
            ELSE FALSE 
          END 
         RETURN n, r, m""")
    result1 = tx.run(query1, attribute=f_attribute, operator=f_operator, value=f_value, graph_name=graph_name)
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
    added_edges = []
    for record in result1:
        edge = record["r"]
        node1 = record["n"]
        node2 = record["m"]
        #print("")
        #print("edge: ", edge, "\n node1:", node1,"'\n node2", node2)
        attributes_n = dict(node1.items())
        attributes_m = dict(node2.items())
        id_n = attributes_n["id"]
        id_m = attributes_m["id"]
        del attributes_n["id"]
        del attributes_m["id"]
        newNode1 = Node(id_n, attributes_n,graph_name)
        newNode2 = Node(id_m, attributes_m,graph_name)
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode1.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode1)

        if edge is not None and (str(newNode2.id) + str(newNode1.id)) not in added_edges:
             newEdge = Edge(newNode1, newNode2)
             newNode1.edges.append(newNode2)
             newGraph.addEdge(newEdge)
             added_edges.append(str(newNode1.id) + str(newNode2.id))
    print("FILTEEEER")
    print(newGraph)
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
       ANY(key IN keys(n) WHERE n[key] CONTAINS $search_query OR key CONTAINS $search_query)
       RETURN n
        """,
        search_query=search_query,
        graph_name=graph_name
    )
    cvorovi=[]
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
            cvorovi.append(newNode)
    added_edges = []
    for record in result:
        edge = record["r"]
        node1 = record["n"]
        node2 = record["m"]
        #print("")
        #print("edge: ", edge, "\n node1:", node1,"'\n node2", node2)
        attributes_n = dict(node1.items())
        attributes_m = dict(node2.items())
        id_n = attributes_n["id"]
        id_m = attributes_m["id"]
        del attributes_n["id"]
        del attributes_m["id"]
        newNode1 = Node(id_n, attributes_n,graph_name)
        newNode2 = Node(id_m, attributes_m,graph_name)
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode1.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode1)

        if edge is not None and (str(newNode2.id) + str(newNode1.id)) not in added_edges:
             newEdge = Edge(newNode1, newNode2)
             newNode1.edges.append(newNode2)
             newGraph.addEdge(newEdge)
             added_edges.append(str(newNode1.id) + str(newNode2.id))
    return newGraph


def search(search_query, attribute, operator, value, graph_name):
    print(search_query)
    print(graph_name)
    print("OPERATORIII")
    print(attribute)
    print(operator)
    print(value)

    new_value = parse_values(value)

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    graphVisualisers = loadPlugins("graph.visualiser")
    with driver.session() as session:
        if(search_query!=""):
            resultSearch = session.read_transaction(search_nodes, search_query, graph_name)
            delete_graph(graph_name)
            write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultSearch)
        resultFilter = session.read_transaction(filter_nodes, attribute, operator, new_value, graph_name)
        delete_graph(graph_name)
        write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultFilter)


        globalni_niz.append(resultFilter)

        stringHTML =  izabrana_opcija(graphVisualisers[1])
        return resultFilter,stringHTML

def parse_values(value):
    try:
        # Pokušajte prvo da parsirate vrednost kao datetime.
        new_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        # Ako to ne uspe, proverite da li se može konvertovati u int ili float.
        try:
            # Pokušajte prvo da konvertujete u int.
            new_value = int(value)
        except ValueError:
            try:
                # Ako to ne uspe, proverite može li se konvertovati u float.
                new_value = float(value)
            except ValueError:
                # Ako ni to ne uspe, vrati originalnu string vrednost.
                new_value = value  # Ovde se pretpostavlja da je value uvek string ako nije datetime, int, ili float.
    return new_value

def get_graph_by_name(graph_name):
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    graphVisualisers = loadPlugins("graph.visualiser")
    with driver.session() as session:
        resultSearch = session.read_transaction(get_graph_by_name_query, graph_name)
    globalni_niz.append(resultSearch)

    stringHTML = izabrana_opcija(graphVisualisers[1])
    return resultSearch,stringHTML
def get_graph_by_name_query(tx, graph_name):
    newGraph = Graph()
    result = tx.run(
        """
        MATCH (n)-[r]-(m)
        WHERE
          (n.graph_name = $graph_name AND m.graph_name = $graph_name)
        RETURN n, r, m
        """,
        graph_name=graph_name
    )
    result1 = tx.run(
        """
       MATCH (n)
       WHERE
       n.graph_name = $graph_name
       RETURN n
        """,
        graph_name=graph_name
    )
    cvorovi=[]
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
            cvorovi.append(newNode)
    added_edges = []
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
        newNode1 = Node(id_n, attributes_n,graph_name)
        newNode2 = Node(id_m, attributes_m,graph_name)
        is_node_in_graph = False
        for indice in newGraph.indices:
            node = indice[0]
            if node.id == newNode1.id:
                is_node_in_graph = True
                break
        if not is_node_in_graph:
            newGraph.addNode(newNode1)
        if edge is not None and (str(newNode2.id) + str(newNode1.id)) not in added_edges:
             newEdge = Edge(newNode1, newNode2)
             newNode1.edges.append(newNode2)
             newGraph.addEdge(newEdge)
             added_edges.append(str(newNode1.id) + str(newNode2.id))
    return newGraph


if __name__ == "__main__":
    main()
