from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    path('search/<int:visualiser>/<int:parser>', views.apply_button, name='search'),
]