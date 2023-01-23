from django.urls import path
from . import views
from . import flights
from . import lounge
from . import reviews
urlpatterns = [
    path('rating/<str:airport>', views.getRoutes, name="airport"),
    path("keywords/<str:route>", views.getWord, name="route"),
    path("comments/<str:portName>", views.change_db, name="comments"),
    path("food/<str:airport>", flights.getFood, name="Food"),
    path("lounge/<str:airport>", lounge.LoungeReviews, name="lounge"),
    path("reviews/<str:airport>", reviews.getReviews, name="reviews")
]
