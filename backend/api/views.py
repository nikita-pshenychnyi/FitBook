import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db.models import Q, Count, Sum, Avg 
from datetime import date, time, datetime 


from .models import Trainer, Section, Booking, Category 


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
    
    categories = Category.objects.prefetch_related('section_set').all()
    
    section_id = request.GET.get('section')
    category_id = request.GET.get('category')  
    search_query = request.GET.get('q')     
    sort_by = request.GET.get('sort')
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    active_section_id = None 
    active_category_id = None 
    
    trainers = Trainer.objects.all()

    if section_id:
        trainers = trainers.filter(section__id=section_id)
        try:
            active_section_id = int(section_id)
            
            section_obj = Section.objects.filter(id=active_section_id).first()
            if section_obj and section_obj.category:
                active_category_id = section_obj.category.id
        except ValueError:
            pass 
    
    elif category_id:
        
        trainers = trainers.filter(section__category__id=category_id)
        try:
            active_category_id = int(category_id)
        except ValueError:
            pass

    if search_query:
        trainers = trainers.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) |
            Q(section__name__icontains=search_query) |
            Q(section__category__name__icontains=search_query)
        )

    if min_price:
        trainers = trainers.filter(price_per_session__gte=min_price)
    if max_price:
        trainers = trainers.filter(price_per_session__lte=max_price)
   
    if sort_by == 'price_asc':
        trainers = trainers.order_by('price_per_session')
    elif sort_by == 'price_desc':
        trainers = trainers.order_by('-price_per_session')

    context = {
        'trainers_list': trainers,
        'categories_list': categories, 
        'active_section_id': active_section_id,
        'active_category_id': active_category_id,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price, 
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
        comment_text = request.POST.get('comment') # <-- ОТРИМУЄМО КОМЕНТАР

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
            comment=comment_text, # <-- ЗБЕРІГАЄМО КОМЕНТАР
            status='pending' 
        )
        messages.success(request, f'Вашу заявку до {trainer.user.get_full_name()} на {booking_date.strftime("%d.%m.%Y")} о {booking_time.strftime("%H:%M")} прийнято!')
        return redirect('profile_page') 

    else:
        context = {
            'trainer': trainer,
            'today_str': date.today().isoformat()
        }
        return render(request, 'booking_form.html', context)


@login_required(login_url='authorization-page')
def profile_page(request):
    sort_by = request.GET.get('sort')
    my_bookings = Booking.objects.filter(user=request.user)

    if sort_by == 'price_asc':
        my_bookings = my_bookings.order_by('trainer__price_per_session')
    elif sort_by == 'price_desc':
        my_bookings = my_bookings.order_by('-trainer__price_per_session')
    elif sort_by == 'date_old':
        my_bookings = my_bookings.order_by('created_at')
    else:
        my_bookings = my_bookings.order_by('-created_at')

    context = { 
        'bookings': my_bookings,
        'current_sort': sort_by 
    }
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


@login_required(login_url='authorization-page')
def statistics_view(request):
    total_bookings = Booking.objects.count()
    revenue_data = Booking.objects.filter(status='confirmed').aggregate(total=Sum('trainer__price_per_session'))
    total_revenue = revenue_data['total'] if revenue_data['total'] else 0
    
    avg_price_data = Trainer.objects.aggregate(avg=Avg('price_per_session'))
    avg_price = round(avg_price_data['avg'], 2) if avg_price_data['avg'] else 0
    
    popular_section = Section.objects.annotate(
        booking_count=Count('trainer__booking')
    ).order_by('-booking_count').first()

    context = {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'avg_price': avg_price,
        'popular_section': popular_section,
    }
    return render(request, 'statistics.html', context)

@login_required(login_url='authorization-page')
def export_bookings_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(40, 40)
    
    textob.setFont("Helvetica-Bold", 14)
    textob.textLine("FitBook: My Bookings Report")
    
    textob.setFont("Helvetica", 12)
    textob.textLine("")

    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    for b in bookings:
        trainer_name = b.trainer.user.username 
        date_str = b.booking_date.strftime("%Y-%m-%d")
        status = b.status
        line = f"Date: {date_str} | Trainer: {trainer_name} | Status: {status}"
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    
    return FileResponse(buf, as_attachment=True, filename='my_bookings.pdf')