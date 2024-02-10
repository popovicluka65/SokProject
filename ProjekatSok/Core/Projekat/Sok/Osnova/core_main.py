from graph_db_service import *
from Projekat.Sok.Osnova.Services.graph import (
    GraphVisualiserBase,
    GraphParserBase
)



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

def search(search_query,graph_name,visualiser, attribute="", operator="", value=""):
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    graphVisualisers = loadPlugins("graph.visualiser")
    with driver.session() as session:
        if(search_query!=""):
            resultSearch = session.read_transaction(search_nodes, search_query, graph_name)
            delete_graph(graph_name)
            write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultSearch)
        if(attribute=="empty"):
            resultFilter = resultSearch
        else:
            new_value = parse_values(value)
            resultFilter = session.read_transaction(filter_nodes, attribute, operator, new_value, graph_name)
            delete_graph(graph_name)
            write_graph_to_neo4j(URI, USERNAME, PASSWORD, resultFilter)

        globalni_niz.append(resultFilter)
        stringHTML =  izabrana_opcija(graphVisualisers[visualiser])
        return resultFilter,stringHTML
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



def initialization():
    delete_all_graphs()
    if len(loadPlugins("graph.parser")) == 0 or len(loadPlugins("graph.visualiser")) == 0:
        return Graph(), ""
    odabraniGraph, stringReprezentaicija = add_workspace(0,0)
    return odabraniGraph, stringReprezentaicija

def add_workspace(parser,visualiser):
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    odabraniGraph = izabrana_opcija(graphParsers[parser])

    add_graph_name(odabraniGraph)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph)
    html = izabrana_opcija(graphVisualisers[visualiser])
    return odabraniGraph, html

def reset_graph(visualiser,parser,workspace):
    graphParsers = loadPlugins("graph.parser")
    graphVisualisers = loadPlugins("graph.visualiser")
    odabraniGraph = izabrana_opcija(graphParsers[parser-1])
    graph_name = "" + str(workspace)
    for node, position in odabraniGraph.indices:
        node.graph_name = graph_name
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, odabraniGraph)
    html = izabrana_opcija(graphVisualisers[visualiser-1])
    return odabraniGraph, html
def parse_values(value):
    try:
        new_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            new_value = float(value)
        except ValueError:
            try:
                new_value = int(value)
            except ValueError:
                new_value = value
    return new_value

def get_graph_by_name(graph_name, visualiser):
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    graphVisualisers = loadPlugins("graph.visualiser")
    with driver.session() as session:
        resultSearch = session.read_transaction(get_graph_by_name_query, graph_name)
    globalni_niz.append(resultSearch)

    stringHTML = izabrana_opcija(graphVisualisers[visualiser])
    return resultSearch,stringHTML



if __name__ == "__main__":
    main()
