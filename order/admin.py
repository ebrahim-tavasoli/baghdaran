from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.db.models.lookups import GreaterThan
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.html import format_html

from order import models
from farmland.models import Farmland
from accounting import models as accounting_models
from .admin_report import OrderReportForm


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
            return queryset.annotate(total_paied=Coalesce(Sum('payments__amount'), 0)).exclude(
                GreaterThan(F('total_price'), F('total_paied')))
        elif value == 'unpaid':
            return queryset.annotate(total_paied=Coalesce(Sum('payments__amount'), 0)).filter(
                GreaterThan(F('total_price'), F('total_paied')))
        return queryset


@admin.register(models.OrderDescription)
class OrderDescriptionAdmin(admin.ModelAdmin):
    list_display = ('fa_name',)
    search_fields = ('fa_name', 'name')
    readonly_fields = ('fa_name', 'created_at', 'updated_at')
    exclude = ('name',)


@admin.register(models.WaterOrder)
class WaterOrderAdmin(admin.ModelAdmin):
    list_display = (
        'number', 'farmland', 'farmland__farmer__name', 'water_source', 'amount', 'water_source_type',
        'created_date_at',
        'valid_date', 'total_price', 'remaining_payment', 'print_button')
    search_fields = ('farmland__name', 'created_date_at', 'farmland__farmer__name', 'farmland__farmer__code_melli')
    list_filter = ('created_date_at', PaymentStatusFilter)
    autocomplete_fields = ('farmland', 'driver', 'water_source')
    readonly_fields = (
        'created_date_at', 'created_time_at', 'updated_at', 'water_price_base', 'pipe_price_base', 'pump_price_base',
        'total_price', 'remaining_payment', 'number')

    inlines = [
        type('PaymentInline', (GenericTabularInline,), {
            'model': accounting_models.Payment,
            'extra': 1,
        }),
    ]

    class Media:
        js = ['admin/js/jquery.init.js', 'admin/js/autocomplete.js']

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['report_url'] = reverse('admin:order_orderreport_changelist')
        return super().changelist_view(request, extra_context=extra_context)

    def print_button(self, obj):
        return format_html(f'<a href="/order/print/water/{obj.id}" target="_blank">چاپ</a>')

    print_button.short_description = 'چاپ'


@admin.register(models.GoodsItem)
class GoodsItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'unit', 'price')
    search_fields = ('name', 'code', 'unit', 'price')
    readonly_fields = ('created_at', 'updated_at')


class GoodsOrderItemsInline(admin.TabularInline):
    model = models.GoodsOrderItem
    fields = ('item', 'quantity', 'discount_type', 'discount')
    readonly_fields = ('price',)
    autocomplete_fields = ('item',)
    extra = 1

    class Media:
        js = ['admin/js/jquery.init.js', 'admin/js/autocomplete.js']


@admin.register(models.GoodsOrder)
class GoodsOrderAdmin(admin.ModelAdmin):
    list_display = (
        'number', 'farmer__name', 'total_price_without_discount',
        'total_price_with_discount', 'total_price_with_tax', 'remaining_payment', 'print_button'
    )
    list_filter = ('created_date_at', PaymentStatusFilter)
    search_fields = ('number', 'farmer__name', 'farmer__code_melli', 'created_date_at')
    readonly_fields = ('created_date_at', 'created_time_at', 'updated_at', 'number')
    autocomplete_fields = ('farmer',)

    inlines = [
        GoodsOrderItemsInline,
        type('PaymentInline', (GenericTabularInline,), {
            'model': accounting_models.Payment,
            'extra': 1,
        }),
   ]

    class Media:
        js = ['admin/js/jquery.init.js', 'admin/js/autocomplete.js']

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['report_url'] = reverse('admin:order_orderreport_changelist')
        return super().changelist_view(request, extra_context=extra_context)

    def print_button(self, obj):
        return format_html(f'<a href="/order/print/goods/{obj.id}" target="_blank">چاپ</a>')

    print_button.short_description = 'چاپ'


class OrderReportAdminView(admin.ModelAdmin):
    change_list_template = "admin/order_report.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report_view), name='order_report'),
        ]
        return custom_urls + urls

    def report_view(self, request):
        form = OrderReportForm(request.GET or None)
        orders = []
        
        if form.is_valid():
            order_type = form.cleaned_data.get('order_type')
            farmland_name = form.cleaned_data.get('farmland')
            farmland_id = request.GET.get('farmland_id')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            
            # Get farmland object if ID is provided
            farmland = None
            if farmland_id:
                try:
                    farmland = Farmland.objects.get(id=farmland_id)
                except Farmland.DoesNotExist:
                    farmland = None
            elif farmland_name:
                # Fallback: try to find farmland by name
                try:
                    farmland = Farmland.objects.get(name=farmland_name)
                except Farmland.DoesNotExist:
                    farmland = None
            
            if order_type == 'water':
                orders = models.WaterOrder.objects.all()
                if farmland:
                    orders = orders.filter(farmland=farmland)
                if start_date:
                    orders = orders.filter(created_date_at__gte=start_date)
                if end_date:
                    orders = orders.filter(created_date_at__lte=end_date)
                    
            elif order_type == 'goods':
                orders = models.GoodsOrder.objects.all()
                if farmland:
                    orders = orders.filter(farmer__farmland=farmland)
                if start_date:
                    orders = orders.filter(created_date_at__gte=start_date)
                if end_date:
                    orders = orders.filter(created_date_at__lte=end_date)
                    
            elif not order_type:  # Show all orders when no type is selected
                water_orders = models.WaterOrder.objects.all()
                goods_orders = models.GoodsOrder.objects.all()
                
                if farmland:
                    water_orders = water_orders.filter(farmland=farmland)
                    goods_orders = goods_orders.filter(farmer__farmland=farmland)
                if start_date:
                    water_orders = water_orders.filter(created_date_at__gte=start_date)
                    goods_orders = goods_orders.filter(created_date_at__gte=start_date)
                if end_date:
                    water_orders = water_orders.filter(created_date_at__lte=end_date)
                    goods_orders = goods_orders.filter(created_date_at__lte=end_date)
                
                # Combine and sort by date
                from itertools import chain
                orders = sorted(
                    chain(water_orders, goods_orders),
                    key=lambda x: x.created_date_at,
                    reverse=True
                )
        
        context = {
            "form": form, 
            "orders": orders,
            "media": form.media,
        }
        return render(request, "admin/order_report.html", context)


# Register the report view as a dummy model to make it accessible in admin
class OrderReport(models.WaterOrder):
    class Meta:
        proxy = True
        verbose_name = "گزارش حواله"
        verbose_name_plural = "گزارش حواله‌ها"


@admin.register(OrderReport)
class OrderReportAdmin(OrderReportAdminView):
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        return self.report_view(request)
