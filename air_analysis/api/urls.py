from django.urls import path
from . import views
from . import flights
from . import lounge
urlpatterns = [
    path('', views.getRoutes, name="route"),
    path("keywords", views.getWord, name="key_route"),
    path("comments", views.change_db, name="commnet"),
    path("food", flights.getFood, name="Food"),
    path("lounge", lounge.getFood, name="lounge")
]
