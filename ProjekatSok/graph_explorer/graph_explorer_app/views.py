from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
sys.path.append("..\..\ProjekatSok\Core\Projekat\Sok\Osnova")
from core_main import *
from django.conf import settings
from .models import *

def index(request):
    graph, stringHTML = django(0,1)
    graph_visualisers = plugin_visualisators()
    plugin_parses = plugin_parsers()
    workspaces = get_unique_graph_names()
    return render(request, 'proba.html', {"graph": stringHTML,'graphVisualisers': graph_visualisers,
                                          'pluginsParsers':plugin_parses,"unique_names":workspaces})

def apply_button(request, visualiser,parser):
    graph,stringHTML=django(parser-1,visualiser-1)
    return HttpResponse(stringHTML, content_type="text/plain")
