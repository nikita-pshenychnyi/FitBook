from django.db import models
from django.contrib.auth.models import User


class Section(models.Model):
    name = models.CharField(max_length=50, verbose_name="Назва секції")
    description = models.TextField(verbose_name="Опис")

    def __str__(self):
        """Цей метод визначає, як об'єкт буде відображатися в адмін-панелі."""
        return self.name


class Trainer(models.Model):
    """Модель для профілю тренера."""
    # Зв'язок "Один-до-одного" (OneToOne) з вбудованою моделлю User.
    # on_delete=models.CASCADE означає: якщо видалити User, профіль тренера теж видалиться.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    # Зв'язок "Багато-до-багатьох" (ManyToMany) з моделлю Section.
    # Один тренер може вести багато секцій, і в одній секції може бути багато тренерів.
    sections = models.ManyToManyField(Section, verbose_name="Секції, які веде тренер")
    
    specialization = models.CharField(max_length=100, verbose_name="Спеціалізація")
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за заняття")

    def __str__(self):
        # В адмінці буде відображатись ім'я користувача, до якого прив'язаний профіль тренера.
        return self.user.get_full_name() or self.user.username


class Booking(models.Model):
    """Модель для заявки на тренування (спрощене бронювання)."""
    STATUS_CHOICES = [
        ('pending', 'В очікуванні'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]

    # Зв'язок "Один-до-багатьох" (ForeignKey). Один User може мати багато заявок.
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    
    # Зв'язок "Один-до-багатьох". Один Trainer може мати багато заявок.
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, verbose_name="Тренер")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заявки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        return f"Заявка від {self.user.username} до {self.trainer.user.username} ({self.status})"