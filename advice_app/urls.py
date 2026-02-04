from django.urls import path
from .views import get_random_advice

urlpatterns = [
    path("api/advice/", get_random_advice, name="get_advice"),
]
