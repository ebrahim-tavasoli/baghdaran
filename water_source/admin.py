from django.contrib import admin
from water_source import models



@admin.register(models.WaterSource)
class WaterSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'operator')
    search_fields = ('name', 'operator')
    readonly_fields = ('created_at', 'updated_at')
