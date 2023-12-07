from typing import List, Union

import pkg_resources
from Projekat.Sok.Osnova.Services.graph import (
    GraphVisualiserBase,
    GraphParserBase
)
from Projekat.Sok.Plagini.graphParserJSON import GraphParserJSON

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
def izabrana_opcija(plugin: Union[GraphVisualiserBase, GraphParserBase], **kwargs):
    try:
        if isinstance(plugin, GraphParserJSON):
            graf = plugin.load("example1.json")
            return graf
        elif isinstance(plugin, GraphVisualiserBase):
            graf = kwargs["graf"]
            return "nije implementirano"
    except Exception as e:
        print(f"Error: {e}")
    return "Radi"


def loadPlugins(pointName: str):
    plugins = []
    for ep in pkg_resources.iter_entry_points(group=pointName):
        # Ucitavanje plagina.
        p = ep.load()
        print(f"{ep.name} {p}")
        # instanciranje odgovarajuce klase
        plugin = p()
        plugins.append(plugin)
    return plugins

def main():
    graphParsers = loadPlugins("graph.parser") #vraca sve parsere sa entri pointom koji se zove graph.parser
    graphVisualisers = loadPlugins("graph.visualiser") #isto za vizualizatore

    consoleMenu(graphParsers=graphParsers,
                graphVisualisers=graphVisualisers)



if __name__ == "__main__":
    main()

