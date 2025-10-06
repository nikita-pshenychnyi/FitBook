from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),

    # Сторінка входу/реєстрації (головна для гостей)
    path('', views.authorization, name='authorization-page'),

    # Маршрути для обробки даних з форм
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Новий маршрут для головної сторінки (для залогінених)
    path('home/', views.home_page, name='home-page'),

    # Залишаємо для майбутнього API, поки не використовуємо
    # path('api/', include('api.urls')),
]