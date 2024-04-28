from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_http_methods
import json
import sys
sys.path.append("..\\venvSok\\Lib\\site-packages\\Projekat\\Sok\\Osnova")

from core_main import *
from django.conf import settings
from .models import *

def index(request):
    graph, stringHTML = initialization()
    graph_visualisers = plugin_visualisators()
    plugin_parses = plugin_parsers()
    workspaces = get_unique_graph_names()
    return render(request, 'view.html', {"graph": stringHTML,'graphVisualisers': graph_visualisers,
                                          'pluginsParsers':plugin_parses,"unique_names":workspaces})

def workspace(request, visualiser,parser):
    graph,stringHTML=add_workspace(parser-1,visualiser-1)
    unique_names = get_unique_graph_names()

    unique_names_json = json.dumps(unique_names)
    stringHTML += f"<script type='text/javascript'>var unique_names = {unique_names_json};</script>"
    return HttpResponse(stringHTML, content_type="text/plain")
@require_http_methods(["POST"])
def apply_button(request):
    try:
        data = json.loads(request.body)
        search_query = data.get('search_query')
        filter_value = data.get('filter')
        workspace = data.get('workspace')
        visualiser = data.get('visualiser')
        parts = filter_value.split(" ")

        graph, stringHTML = search(search_query,workspace,visualiser, *parts)
        return HttpResponse(stringHTML, content_type="text/plain")
    except Exception as e:
        return HttpResponse(status=400, content='Bad Request: ' + str(e))
def view_workspace(request, workspace, visualiser):
    graph, stringHTML = get_graph_by_name(workspace, visualiser)
    return HttpResponse(stringHTML, content_type="text/plain")
def reset(request,visualiser,parser,workspace):
    graph, stringHTML = reset_graph(visualiser,parser,workspace)
    return HttpResponse(stringHTML, content_type="text/plain")
