from django.contrib import admin
from .models import Section, Trainer, Booking, Category  # <-- Додав імпорт Category

admin.site.register(Category)
admin.site.register(Section)
admin.site.register(Trainer)
admin.site.register(Booking)