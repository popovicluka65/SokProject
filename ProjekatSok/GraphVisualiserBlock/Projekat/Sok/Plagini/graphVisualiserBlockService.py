from jinja2 import Environment, FileSystemLoader, Template
import os
def get_absolute_path():
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "..","..", "template")
def blockVisualize(graph):
    template_dir=get_absolute_path()
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("block_visualizer.html")
    points = []
    for node in graph.indices:
        points.append(node[0])
    return template.render(points=points, edges=graph.edges)