from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Імпортуємо декоратор, який буде перевіряти, чи залогінений користувач
from django.contrib.auth.decorators import login_required

# Сторінка входу/реєстрації
def authorization(request):
    # Якщо користувач вже залогінений, перенаправляємо його на головну
    if request.user.is_authenticated:
        return redirect('home-page')
    return render(request, 'index.html')

# Сторінка "Про нас" (залишаємо для прикладу)
def about(request):
    return HttpResponse("<h1>About Page</h1>")

# Функція реєстрації
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
            username=email, # Використовуємо email як унікальний username
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        # Автоматично логінимо користувача після реєстрації
        login(request, user)
        messages.success(request, f'Вітаємо, {user.first_name}!')
        # Перенаправляємо на нову головну сторінку
        return redirect('home-page')
    else:
        return redirect('authorization-page')

# Функція входу
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'З поверненням, {user.first_name}!')
            # Перенаправляємо на нову головну сторінку
            return redirect('home-page') 
        else:
            messages.error(request, 'Неправильний email або пароль.')
            return redirect('authorization-page')
    else:
        return redirect('authorization-page')

# Нова функція виходу
def logout_user(request):
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('authorization-page')


# Нова головна сторінка сайту (тільки для залогінених)
@login_required(login_url='authorization-page')
def home_page(request):
    return render(request, 'home.html')
