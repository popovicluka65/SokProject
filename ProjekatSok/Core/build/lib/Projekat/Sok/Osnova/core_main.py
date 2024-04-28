from graph_db_service import *
from Projekat.Sok.Osnova.Services.graph import (
    GraphVisualiserBase,
    GraphParserBase
)

def consoleMenu(*args, **kwargs):
    plugins: List[Union] = kwargs.get("graphParsers", []) + kwargs.get("graphVisualisers",[])  # ovde treba da ide typing Union[GraphParserBase, GraphVisualiserBase] ali za sad ne
    if not plugins:
        print("No plugins were recognized!")
        return
    error = False
    message = None
    while True:
        print("-----------------------------------")
        if error:
            print("Incorrect value entered")
            error = False
        if message:
            print(message)
        print("Options: ")
        for i, plugin in enumerate(plugins):
            print(f"{i} {plugin.identifier()}")
        print(f"{len(plugins)} for exit")
        try:
            choice = int(input("Select number of option:"))
        except:
            error = True
            continue
        if choice == len(plugins):
            return
        elif 0 <= choice < len(plugins):
            poruka = selected_option(plugins[choice], **kwargs)
        else:
            error = True
    return ""

def selected_option(plugin: Union[GraphVisualiserBase, GraphParserBase], **kwargs):
    global global_array
    try:
        if isinstance(plugin, GraphParserBase):
            if (type(plugin).__name__ == "GraphParserRDF"):
                graf = plugin.load("example1.ttl")
            else:
                graf = plugin.load("example1.json")
            global_array.append(graf)
            return graf
        if isinstance(plugin, GraphVisualiserBase):
            return plugin.visualize(global_array[-1])
    except Exception as e:
        print(f"Error: {e}")
    return "Do"


def load_plugins(pointName: str):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=pointName):
        p = ep.load()
        print(f"{ep.name} {p}")
        plugin = p()
        plugins.append(plugin)
    return plugins

def search(search_query,graph_name,visualiser, attribute="", operator="", value=""):
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    graph_visualisers = load_plugins("graph.visualiser")
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

        global_array.append(resultFilter)
        stringHTML =  selected_option(graph_visualisers[visualiser])
        return resultFilter,stringHTML
def plugin_visualisators():
    graphVisualisers = load_plugins("graph.visualiser")
    plugin_names = [type(plugin).__name__ for plugin in graphVisualisers]
    return plugin_names

def plugin_parsers():
    graphVisualisers = load_plugins("graph.parser")
    plugin_names = [type(plugin).__name__ for plugin in graphVisualisers]
    return plugin_names

def main():
    graphParsers = load_plugins("graph.parser")
    graphVisualisers = load_plugins("graph.visualiser")

    consoleMenu(graphParsers=graphParsers,
                graphVisualisers=graphVisualisers,
                file="example1.json")

def initialization():
    delete_all_graphs()
    if len(load_plugins("graph.parser")) == 0 or len(load_plugins("graph.visualiser")) == 0:
        return Graph(), ""
    selected_graph, string_representation = add_workspace(0,0)
    return selected_graph, string_representation

def add_workspace(parser,visualiser):
    graph_parsers = load_plugins("graph.parser")
    graph_visualisers = load_plugins("graph.visualiser")
    selected_graph = selected_option(graph_parsers[parser])

    add_graph_name(selected_graph)
    write_graph_to_neo4j(URI, USERNAME, PASSWORD,selected_graph)
    html = selected_option(graph_visualisers[visualiser])
    return selected_graph, html

def reset_graph(visualiser,parser,workspace):
    graph_parsers = load_plugins("graph.parser")
    graph_visualisers = load_plugins("graph.visualiser")
    selected_graph = selected_option(graph_parsers[parser-1])
    graph_name = "" + str(workspace)
    for node, position in selected_graph.indices:
        node.graph_name = graph_name
    write_graph_to_neo4j(URI, USERNAME, PASSWORD, selected_graph)
    html = selected_option(graph_visualisers[visualiser-1])
    return selected_graph, html
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
    graph_visualisers = load_plugins("graph.visualiser")
    with driver.session() as session:
        result_search = session.read_transaction(get_graph_by_name_query, graph_name)
    global_array.append(result_search)

    string_html = selected_option(graph_visualisers[visualiser])
    return result_search,string_html

if __name__ == "__main__":
    main()
