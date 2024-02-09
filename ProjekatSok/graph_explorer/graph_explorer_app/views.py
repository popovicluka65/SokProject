from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import json
import sys
sys.path.append("..\..\ProjekatSok\Core\Projekat\Sok\Osnova")
from core_main import *
from django.conf import settings
from .models import *

def index(request):
    graph, stringHTML = initialization(0,0)

    graph_visualisers = plugin_visualisators()
    plugin_parses = plugin_parsers()
    workspaces = get_unique_graph_names()
    return render(request, 'proba.html', {"graph": stringHTML,'graphVisualisers': graph_visualisers,
                                          'pluginsParsers':plugin_parses,"unique_names":workspaces})


def workspace(request, visualiser,parser):
    graph,stringHTML=add_workspace(parser-1,visualiser-1)
    unique_names = get_unique_graph_names()

    unique_names_json = json.dumps(unique_names)
    stringHTML += f"<script type='text/javascript'>var unique_names = {unique_names_json};</script>"
    return HttpResponse(stringHTML, content_type="text/plain")

def apply_button(request, search_query,filter,workspace):
    parts = filter.split(" ")
    graph,stringHTML = search(search_query, parts[0],parts[1],parts[2],workspace)
    return HttpResponse(stringHTML, content_type="text/plain")
