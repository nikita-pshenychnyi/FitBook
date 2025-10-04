from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name = 'Api-home'),
    path('about/', views.about, name = 'Api-about'),
]
