from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_view, name='search'),
    path('image/', views.image_search, name='image_search'),
    path('suggestions/', views.suggestions, name='suggestions'),
    path('stats/', views.stats_view, name='stats'),
]
