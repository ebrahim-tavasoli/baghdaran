from django.contrib import admin
from accounting import models

@admin.register(models.Price)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("fa_name", "value")
    search_fields = ("name", "fa_name")
    readonly_fields = ("updated_at", "fa_name")
    ordering = ("-updated_at",)
    exclude = ('name',)
    