from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('api/', views.about ),
    path('export_pdf/', views.export_bookings_pdf, name='export_pdf'),
]