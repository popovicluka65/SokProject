from typing import List, Union

import pkg_resources

from Projekat.Sok.Osnova.Services.graph import (
    GraphVisualiserBase,
    GraphParserBase
)

globalni_niz = []

html_string = """
<!DOCTYPE html>
<meta charset="utf-8" />
<style>
  .links line {
    stroke: #999;
    stroke-opacity: 0.6;
  }

  .nodes circle {
    stroke: #fff;
    stroke-width: 1.5px;
    fill: red;
  }

  .labels text {
    font-size: 20px;
    font-family: Arial, Helvetica, sans-serif;
    font-weight: bold;
    fill: black;
  }
</style>

<svg width="1800" height="800"></svg>
<script src="https://d3js.org/d3.v4.min.js"></script>

<script>
  var svg = d3.select("svg");
  var width = svg.attr("width");
  var height = svg.attr("height");

  var graph = {
    nodes: [

        {id: "1"},

        {id: "2"},

        {id: "3"},

    ],
    links: [

        {source: "1", target: "2" },

        {source: "1", target: "3" },

        {source: "2", target: "1" },

        {source: "3", target: "1" },

    ]
  };

  var simulation = d3
  .forceSimulation(graph.nodes)
  .force(
    "link",
    d3
      .forceLink()
      .id(function(d) {
        return d.id;
      })
      .links(graph.links).distance(100)
  )
  .force("charge", d3.forceManyBody().strength(-30))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .on("tick", ticked);

  var text = svg
    .append("g")
    .attr("class", "labels")
    .selectAll("text")
    .data(graph.nodes)
    .enter()
    .append("text")
    .text(function(d) {
      return d.id;
    })
    .attr("dx", 12) 
    .attr("dy", ".35em")

   var link = svg
  .append("g")
  .attr("class", "links")
  .selectAll("line")
  .data(graph.links)
  .enter()
  .append("line")
  .attr("stroke-width", function(d) {
    return 3;
  })

  var node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter()
    .append("circle")
    .attr("r", 10)
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );

  function ticked() {
    link
    .attr("x1", function(d) {
      return d.source.x;
    })
    .attr("y1", function(d) {
      return d.source.y;
    })
    .attr("x2", function(d) {
      return d.target.x;
    })
    .attr("y2", function(d) {
      return d.target.y;
    });

  node
    .attr("cx", function(d) {
      return d.x;
    })
    .attr("cy", function(d) {
      return d.y;
    });

  text
    .attr("x", function(d) {
      return d.x;
    })
    .attr("y", function(d) {
      return d.y;
    });
}

  function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
</script>
"""


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
            graf = plugin.load("example1.ttl")
            globalni_niz.append(graf)
            return graf
        if isinstance(plugin, GraphVisualiserBase):
            #plugin.visualize(globalni_niz[-1])
            #return plugin.visualize(globalni_niz[-1])
            return html_string
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
    stringReprezentaicija = izabrana_opcija(graphVisualisers[1])
    return odabraniGraph,stringReprezentaicija

if __name__ == "__main__":
    main()
