from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.template.loader import render_to_string

from baghdaran.logics import return_pdf
from order import models


class PrintOrderView(View):
    def get(self, request, order_type, order_id, *args, **kwargs):
        if order_type == 'water':
            order = get_object_or_404(models.WaterOrder, id=order_id)
            description = get_object_or_404(models.OrderDescription, name='water_order_liter').template if order.water_source_type == 'liter' else get_object_or_404(models.OrderDescription, name='water_order_pipe').template
            template = 'order/water_order_liter.html' if order.water_source_type == 'liter' else 'order/water_order_pipe.html'
            filename = f"water_order_{order.id}.pdf"
            context = {
                'created_at': order.created_date_at,
                'order': order,
                'description': description,
            }
        else:
            raise Http404("Invalid order type")
        html_content = render_to_string(template, context)
        return return_pdf(html_content, filename)