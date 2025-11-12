from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),

   
    path('', views.authorization, name='authorization-page'),

   
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

   
    path('home/', views.home_page, name='home-page'),

    # Залишаємо для майбутнього API, поки не використовуємо
    # path('api/', include('api.urls')),
]