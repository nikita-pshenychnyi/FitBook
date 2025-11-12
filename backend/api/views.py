# api/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required # <-- (1) Поки що не потрібно

# (!!!) 1. Імпортуй свої моделі, щоб отримати до них доступ
from .models import Trainer, Section 

#
# --- ТВОЯ ЛОГІКА АВТЕНТИФІКАЦІЇ (ТУТ ВСЕ ПРАВИЛЬНО) ---
#

def authorization(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    return render(request, 'index.html')

def about(request):
    return HttpResponse("<h1>About Page</h1>")

def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('name')
        last_name = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password-confirm')

        if password != password_confirm:
            messages.error(request, 'Паролі не збігаються!')
            return redirect('authorization-page')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Користувач з таким email вже існує!')
            return redirect('authorization-page')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        login(request, user)
        messages.success(request, f'Вітаємо, {user.first_name}!')
        return redirect('home-page')
    else:
        return redirect('authorization-page')

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'З поверненням, {user.first_name}!')
            return redirect('home-page') 
        else:
            messages.error(request, 'Неправильний email або пароль.')
            return redirect('authorization-page')
    else:
        return redirect('authorization-page')

def logout_user(request):
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('authorization-page')


#
# --- ГОЛОВНА СТОРІНКА (Ось зміни) ---
#

# (1) Я прибрав @login_required. Тепер сторінку бачать ВСІ.
def home_page(request):
    
    # (2) Отримуємо ВСІХ тренерів з бази даних
    trainers = Trainer.objects.all()
    
    # (3) Отримуємо ВСІ секції (для майбутніх фільтрів)
    sections = Section.objects.all()

    # (4) Створюємо "контекст" - словник, який поїде в HTML
    context = {
        'trainers_list': trainers,   # <-- Передаємо список тренерів
        'sections_list': sections,  # <-- Передаємо список секцій
    }
    
    # (5) Відмальовуємо 'home.html' і передаємо туди context
    return render(request, 'home.html', context)