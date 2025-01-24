from django.contrib import admin
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.db.models.lookups import GreaterThan
from django.urls import reverse
from django.utils.html import format_html


from order import models
from accounting import models as accounting_models


class PaymentStatusFilter(admin.SimpleListFilter):
    title = 'وضعیت تسویه'
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('paid', 'تسویه شده'),
            ('unpaid', 'تسویه نشده'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'paid':
            return queryset.annotate(total_paied=Coalesce(Sum('order_payments__amount'), 0)).exclude(GreaterThan(F('total_price'), F('total_paied')))
        elif value == 'unpaid':
            return queryset.annotate(total_paied=Coalesce(Sum('order_payments__amount'), 0)).filter(GreaterThan(F('total_price'), F('total_paied')))
        return queryset

@admin.register(models.OrderDescription)
class OrderDescriptionAdmin(admin.ModelAdmin):
    list_display = ('fa_name',)
    search_fields = ('fa_name', 'name')
    readonly_fields = ('fa_name', 'created_at', 'updated_at')
    exclude = ('name',)

@admin.register(models.WaterOrder)
class WaterOrderAdmin(admin.ModelAdmin):
    list_display = ('farmland', 'farmland__farmer__name', 'water_source', 'amount', 'water_source_type', 'created_date_at', 'valid_date', 'total_price', 'remaining_payment', 'print_button')
    search_fields = ('farmland__name', 'created_date_at', 'farmland__farmer__name', 'farmland__farmer__code_melli')
    list_filter = ('created_date_at', PaymentStatusFilter)
    autocomplete_fields = ('farmland', 'driver', 'water_source')
    readonly_fields = ('created_date_at', 'created_time_at', 'updated_at', 'water_price_base', 'pipe_price_base', 'pump_price_base', 'total_price', 'remaining_payment')

    inlines = [
        type('PaymentInline', (admin.TabularInline,), {
            'model': accounting_models.Payment,
            'extra': 1,
        }),
    ]

    class Media:
        js = ['admin/js/jquery.init.js', 'admin/js/autocomplete.js']
    
    def print_button(self, obj):
        return format_html(f'<a href="/order/print/water/{obj.id}" target="_blank">چاپ</a>')

    print_button.short_description = 'چاپ'
