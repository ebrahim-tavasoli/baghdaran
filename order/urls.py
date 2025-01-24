from django.urls import path

from order import views


urlpatterns = [
    path('print/<str:order_type>/<int:order_id>/', views.PrintOrderView.as_view(), name='print_order'),
]
