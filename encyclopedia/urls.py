from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/", views.index, name="wiki"),
    path("wiki/<str:title>", views.page, name="page"),
    path("w/search/", views.searchField, name="searchField"),
    path("w/new_page", views.new, name="new"),
    path("w/edit_page/<str:title>", views.edit, name="edit"),
    path("w/random", views.random, name="random"),
    path("w/error/<str:errortype>/<str:title>", views.error, name="error")
]
