from django.contrib import admin

from farmland import models


@admin.register(models.Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_melli', 'phone')
    search_fields = ('name', 'code_melli', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        type('FarmlandInline', (admin.TabularInline,), {
            'model': models.Farmland,
            'extra': 1,
        }),
    ]


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(models.Farmland)
class FarmlandAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'zone')
    search_fields = ('name', 'address', 'farmer__name', 'farmer__code_melli')
    list_filter = ('zone__name',)
    autocomplete_fields = ('farmer', 'zone')
    readonly_fields = ('created_at', 'updated_at')
    class Media:
        js = ['admin/js/jquery.init.js', 'admin/js/autocomplete.js']


@admin.register(models.FarmlandType)
class FarmlandTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    