from django.urls import path

from food.views import home

urlpatterns = [
    path("", home, name="home"),
]
