

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 


from .models import Trainer, Section, Booking 
from datetime import date, time, datetime 



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


@login_required(login_url='authorization-page')
def home_page(request):
    sections = Section.objects.all()
    section_id = request.GET.get('section')
    active_section_id = None 
    if section_id:
        trainers = Trainer.objects.filter(sections__id=section_id)
        try:
            active_section_id = int(section_id) 
        except ValueError:
            pass
    else:
        trainers = Trainer.objects.all()
    context = {
        'trainers_list': trainers,
        'sections_list': sections,
        'active_section_id': active_section_id
    }
    return render(request, 'home.html', context)


@login_required(login_url='authorization-page')
def booking_page(request, pk):
   
    try:
        trainer = Trainer.objects.get(pk=pk)
    except Trainer.DoesNotExist:
        messages.error(request, 'Такого тренера не існує.')
        return redirect('home-page')

    
    MIN_TIME = time(8, 0)  
    MAX_TIME = time(21, 0) 

   
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')

        
        try:
            booking_date = date.fromisoformat(date_str)
            booking_time = time.fromisoformat(time_str)
        except (ValueError, TypeError):
            messages.error(request, 'Невірний формат дати або часу.')
            return redirect('booking_page', pk=trainer.pk) 
        
        if booking_date < date.today():
            messages.error(request, 'Ви не можете обрати дату в минулому.')
            return redirect('booking_page', pk=trainer.pk)
        
        
        if not (MIN_TIME <= booking_time <= MAX_TIME):
            messages.error(request, f'Будь ласка, оберіть час між {MIN_TIME.strftime("%H:%M")} та {MAX_TIME.strftime("%H:%M")}.')
            return redirect('booking_page', pk=trainer.pk)

        
        Booking.objects.create(
            user=request.user,
            trainer=trainer,
            booking_date=booking_date,
            booking_time=booking_time,
            status='pending' 
        )
        messages.success(request, f'Вашу заявку до {trainer.user.get_full_name()} на {booking_date.strftime("%d.%m.%Y")} о {booking_time.strftime("%H:%M")} прийнято!')
        return redirect('profile_page') 

    
    else:
       
        context = {
            'trainer': trainer,
            'today_str': date.today().isoformat() # "2025-11-14"
        }
        return render(request, 'booking_form.html', context)



@login_required(login_url='authorization-page')
def profile_page(request):
    my_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    context = { 'bookings': my_bookings }
    return render(request, 'profile.html', context)


@login_required(login_url='authorization-page')
def delete_booking(request, pk):
    try:
        booking_to_delete = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        messages.error(request, 'Такої заявки не існує.')
        return redirect('profile_page')
    if request.user != booking_to_delete.user:
        messages.error(request, 'Ви не можете видалити чужу заявку.')
        return redirect('profile_page')
    booking_to_delete.delete()
    messages.success(request, 'Вашу заявку скасовано.')
    return redirect('profile_page')