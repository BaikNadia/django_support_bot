from django.urls import path
from .views import (
    get_random_advice,
    home,
    random_advice_page,
    all_advice,
    category_advice,
    advice_detail,
    about,
    license_page
)

urlpatterns = [
    # API
    path('api/advice/', get_random_advice, name='get_advice'),

    # Веб-страницы
    path('', home, name='home'),
    path('random/', random_advice_page, name='random_advice'),
    path('all/', all_advice, name='all_advice'),
    path('category/<str:category>/', category_advice, name='category_advice'),
    path('advice/<int:id>/', advice_detail, name='advice_detail'),
    path('about/', about, name='about'),
    path('license/', license_page, name='license'),
]
