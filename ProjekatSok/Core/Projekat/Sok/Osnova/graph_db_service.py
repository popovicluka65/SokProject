from datetime import datetime
from typing import List, Union
import uuid
from Projekat.Sok.Osnova.Model.graph import Graph as Graph, Node, Edge
import pkg_resources
from neo4j import GraphDatabase
from neomodel import db

global_array = []

URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

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
        WHEN $operator = '>=' THEN n[$attribute] >= $value 
        WHEN $operator = '<=' THEN n[$attribute] <= $value 
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
            WHEN $operator = '>=' THEN n[$attribute] < $value AND m[$attribute] >= $value
            WHEN $operator = '<=' THEN n[$attribute] < $value AND m[$attribute] <= $value
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
    return newGraph

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
def add_graph_name(graph: Graph):
    graph_name=""+str(uuid.uuid4())
    for node, position in graph.indices:
        node.graph_name =graph_name
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
def retrieve_graph(tx):
    result = tx.run(
        "MATCH (n) OPTIONAL MATCH (n)-[r]-(m) RETURN COLLECT(DISTINCT n) AS nodes, COLLECT(DISTINCT r) AS relationships")
    return result.data()
def findNodeByDict(g,nodeDict):
        for node,possition in g.indices:
            if node.value==nodeDict:
                return node
