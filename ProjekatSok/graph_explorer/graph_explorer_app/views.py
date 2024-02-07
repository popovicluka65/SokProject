from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import sys
sys.path.append("..\..\ProjekatSok\Core\Projekat\Sok\Osnova")
from core_main import *
from django.conf import settings
from .models import *

def index(request):
    graph, stringHTML = django()
    graph_visualisers = plugin_visualisators()
    plugin_parses = plugin_parsers()
    return render(request, 'proba.html', {"graph": stringHTML,'graphVisualisers': graph_visualisers,
                                          'pluginsParsers':plugin_parses})
