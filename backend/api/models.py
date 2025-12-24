from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name") 

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"          
        verbose_name_plural = "Categories"


class Section(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва секції")
    description = models.TextField(verbose_name="Опис", blank=True, null=True)
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        verbose_name="Категорія"
    )

    def __str__(self):
        return self.name


class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    section = models.ForeignKey(
        Section, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Секція"
    )
 
    specialization = models.CharField(max_length=255, verbose_name="Спеціалізація") 
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за заняття")

    photo = models.ImageField(
        upload_to="trainers/", 
        null=True, 
        blank=True, 
        verbose_name="Фото"
    )

 
    experience = models.PositiveIntegerField(
        verbose_name="Стаж роботи (років)", 
        default=1,
        help_text="Вкажіть кількість років досвіду"
    )
   
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В очікуванні'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name="Тренер")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заявки")
    booking_date = models.DateField(verbose_name="Дата заняття")
    booking_time = models.TimeField(verbose_name="Час заняття")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

  
    comment = models.TextField(
        verbose_name="Коментар клієнта", 
        blank=True, 
        null=True
    )

    def __str__(self):
        return f"Заявка від {self.user.username} до {self.trainer.user.username} ({self.status})"