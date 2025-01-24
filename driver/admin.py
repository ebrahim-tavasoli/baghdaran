from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'car_number')
    search_fields = ('name', 'phone', 'car_number')
    readonly_fields = ('created_at', 'updated_at')
