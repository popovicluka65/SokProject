from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('workspace/<int:visualiser>/<int:parser>', views.workspace, name='workspace'),
    path('search/', views.apply_button, name='search'),
    path('view-workspace/<str:workspace>/<int:visualiser>', views.view_workspace, name='workspace'),
    path('reset/<int:visualiser>/<int:parser>/<str:workspace>', views.reset, name='reset'),
]