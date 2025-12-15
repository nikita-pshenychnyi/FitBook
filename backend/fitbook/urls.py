from django.contrib import admin
from django.urls import path, include
from api import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    
   
    path('', views.authorization, name='authorization-page'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    
    path('home/', views.home_page, name='home-page'),
    path('profile/', views.profile_page, name='profile_page'),
    path('book/trainer/<int:pk>/', views.booking_page, name='booking_page'),
    path('booking/delete/<int:pk>/', views.delete_booking, name='delete_booking'),

    
    path('statistics/', views.statistics_view, name='statistics'),
    path('export_pdf/', views.export_bookings_pdf, name='export_pdf'),
]  


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)