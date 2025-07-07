from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.http import JsonResponse
from django.views import View
from django.template.loader import render_to_string
from django.db.models import Sum
from farmland.models import Farmland
from order.models import WaterOrder, GoodsOrder
from order.widgets import JalaliDatePickerWidget, FarmlandAutocompleteWidget
from baghdaran.logics import return_pdf
import datetime

class OrderReportForm(forms.Form):
    ORDER_TYPE_CHOICES = [
        ("", "همه"),
        ("water", "حواله آب"),
        ("goods", "حواله نهاده")
    ]
    order_type = forms.ChoiceField(
        choices=ORDER_TYPE_CHOICES, 
        required=False, 
        label="نوع حواله"
    )
    farmland = forms.CharField(
        required=False, 
        label="مزرعه",
        widget=FarmlandAutocompleteWidget(),
        help_text="شروع به تایپ کنید تا نتایج نمایش داده شود"
    )
    
    start_date = forms.DateField(
        required=False, 
        label="از تاریخ",
        widget=JalaliDatePickerWidget(attrs={
            'placeholder': 'مثال: 1403-01-15'
        }),
        help_text="تاریخ شروع بازه گزارش"
    )
    end_date = forms.DateField(
        required=False, 
        label="تا تاریخ",
        widget=JalaliDatePickerWidget(attrs={
            'placeholder': 'مثال: 1403-12-29'
        }),
        help_text="تاریخ پایان بازه گزارش"
    )
    
    class Media:
        css = {
            'all': ('admin/css/widgets.css',),
        }
        js = [
            'admin/js/core.js',
            'admin/js/admin/RelatedObjectLookups.js',
            'admin/js/jquery.init.js',
            'admin/js/actions.js',
        ]


class FarmlandAutocompleteView(View):
    """
    AJAX view for farmland autocomplete search
    """
    def get(self, request):
        term = request.GET.get('term', '')
        if len(term) < 2:  # Require at least 2 characters
            return JsonResponse({'results': []})
        
        # Search farmlands that have either WaterOrders or GoodsOrders (via farmers)
        from django.db.models import Q
        from farmland.models import Farmer
        
        # Get farmlands that have water orders
        water_farmlands = Farmland.objects.filter(
            name__icontains=term,
            waterorder__isnull=False
        ).distinct().values('id', 'name')
        
        # Get farmlands that have goods orders (through farmers)
        goods_farmlands = Farmland.objects.filter(
            name__icontains=term,
            farmer__goodsorder__isnull=False
        ).distinct().values('id', 'name')
        
        # Combine and remove duplicates
        all_farmlands = {}
        for farmland in water_farmlands:
            all_farmlands[farmland['id']] = farmland
        for farmland in goods_farmlands:
            all_farmlands[farmland['id']] = farmland
            
        # If no orders found, just show all matching farmlands
        if not all_farmlands:
            all_farmlands_query = Farmland.objects.filter(
                name__icontains=term
            ).values('id', 'name')[:10]
            for farmland in all_farmlands_query:
                all_farmlands[farmland['id']] = farmland
        
        results = [
            {
                'id': farmland['id'],
                'text': farmland['name']
            }
            for farmland in list(all_farmlands.values())[:10]
        ]
        
        return JsonResponse({'results': results})


class OrderReportPDFView(View):
    """
    View to generate PDF report of orders
    """
    def get(self, request):
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
                try:
                    farmland = Farmland.objects.get(name=farmland_name)
                except Farmland.DoesNotExist:
                    farmland = None
            
            # Apply the same filtering logic as the main report view
            if order_type == 'water':
                orders = WaterOrder.objects.all()
                if farmland:
                    orders = orders.filter(farmland=farmland)
                if start_date:
                    orders = orders.filter(created_date_at__gte=start_date)
                if end_date:
                    orders = orders.filter(created_date_at__lte=end_date)
                    
            elif order_type == 'goods':
                orders = GoodsOrder.objects.all()
                if farmland:
                    orders = orders.filter(farmer__farmland=farmland)
                if start_date:
                    orders = orders.filter(created_date_at__gte=start_date)
                if end_date:
                    orders = orders.filter(created_date_at__lte=end_date)
                    
            elif not order_type:  # Show all orders when no type is selected
                water_orders = WaterOrder.objects.all()
                goods_orders = GoodsOrder.objects.all()
                
                if farmland:
                    water_orders = water_orders.filter(farmland=farmland)
                    goods_orders = goods_orders.filter(farmer__farmland=farmland)
                if start_date:
                    water_orders = water_orders.filter(created_date_at__gte=start_date)
                    goods_orders = goods_orders.filter(created_date_at__gte=start_date)
                if end_date:
                    water_orders = water_orders.filter(created_date_at__lte=end_date)
                    goods_orders = goods_orders.filter(created_date_at__lte=end_date)
                
                # Combine orders
                orders = list(water_orders) + list(goods_orders)
                orders.sort(key=lambda x: x.created_date_at, reverse=True)
        
        # Calculate totals
        total_amount = sum(order.total_price for order in orders)
        total_remaining = sum(order.remaining_payment for order in orders)
        
        # Prepare filter info for template
        filter_info = {
            'order_type': order_type,
            'order_type_display': dict(OrderReportForm.ORDER_TYPE_CHOICES).get(order_type, ''),
            'farmland': farmland.name if farmland else farmland_name,
            'start_date': start_date,
            'end_date': end_date,
        }
        
        context = {
            'orders': orders,
            'filter_info': filter_info,
            'total_amount': total_amount,
            'total_remaining': total_remaining,
            'current_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        
        html_content = render_to_string('order/order_report_pdf.html', context)
        filename = f"order_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return return_pdf(html_content, filename)
