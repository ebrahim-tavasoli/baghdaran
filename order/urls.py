from django.urls import path

from order import views
from order.admin_report import FarmlandAutocompleteView, OrderReportPDFView


urlpatterns = [
    path('print/<str:order_type>/<int:order_id>/', views.PrintOrderView.as_view(), name='print_order'),
    path('ajax/farmland-autocomplete/', FarmlandAutocompleteView.as_view(), name='farmland_autocomplete'),
    path('report/pdf/', OrderReportPDFView.as_view(), name='order_report_pdf'),
]
