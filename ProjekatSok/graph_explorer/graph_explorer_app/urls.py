from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    #path('search/<int:visualiser>/<int:parser>/<str:search>/<str:filter>', views.apply_button, name='search'),
    path('workspace/<int:visualiser>/<int:parser>', views.workspace, name='workspace'),
    path('search/<str:search_query>/<str:filter>/<str:workspace>', views.apply_button, name='search'),
]