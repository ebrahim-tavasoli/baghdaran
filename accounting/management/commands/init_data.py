import jdatetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from accounting.models import Price
from order.models import OrderDescription, OrderNumber


class Command(BaseCommand):
    help = 'Initialize default data for the application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data initialization...')

        default_user_groups = {
                'manager': [
                    'add_farmer',
                    'change_farmer',
                    'delete_farmer',
                    'view_farmer',

                    'add_farmlandtype',
                    'change_farmlandtype',
                    'delete_farmlandtype',
                    'view_farmlandtype',

                    'add_zone',
                    'change_zone',
                    'delete_zone',
                    'view_zone',

                    'add_farmland',
                    'change_farmland',
                    'delete_farmland',
                    'view_farmland',

                    'add_waterorder',
                    'change_waterorder',
                    'delete_waterorder',
                    'view_waterorder',

                    'change_orderdescription',
                    'view_orderdescription',

                    'add_watersource',
                    'change_watersource',
                    'delete_watersource',
                    'view_watersource',

                    'add_driver',
                    'change_driver',
                    'delete_driver',
                    'view_driver',

                    'change_price',
                    'view_price',

                    'add_payment',
                    'change_payment',
                    'delete_payment',
                    'view_payment',
                ],
                'staff': [
                    'add_farmer',
                    'change_farmer',
                    'delete_farmer',
                    'view_farmer',

                    'add_farmland',
                    'change_farmland',
                    'delete_farmland',
                    'view_farmland',

                    'add_waterorder',
                    'change_waterorder',
                    'view_waterorder',

                    'add_driver',
                    'change_driver',
                    'delete_driver',
                    'view_driver',
                    
                    'add_payment',
                    'view_payment',
                ]
            }

        default_prices = [
            {'name': 'water_price_liter', 'value': 1000, 'fa_name': 'قیمت هر لیتر آب'},
            {'name': 'water_price_time', 'value': 100000, 'fa_name': 'قیمت هر ساعت آب'},
            {'name': 'pipe_price_fix', 'value': 50000, 'fa_name': 'قیمت ثابت لوله'},
            {'name': 'pipe_price_dynamic', 'value': 1000, 'fa_name': 'قیمت هر ۵ متر لوله'},
            {'name': 'pump_price', 'value': 100000, 'fa_name': 'قیمت هر پمپاژ'},
        ]

        default_descriptions = [
            {'name': 'water_order_liter', 'fa_name': 'توضیحات حواله آب تانکری'},
            {'name': 'water_order_pipe', 'fa_name': 'توضیحات حواله آب ساعتی'},
        ]

        for group_name, permissions in default_user_groups.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for permission in permissions:
                perm_obj = Permission.objects.get(codename=permission)
                group.permissions.add(perm_obj)

        prices = []
        for price_data in default_prices:
            prices.append(Price(
                **price_data
            ))
        Price.objects.bulk_create(prices, ignore_conflicts=True)

        descriptions = []
        for description_data in default_descriptions:
            descriptions.append(OrderDescription(
                **description_data
            ))
        OrderDescription.objects.bulk_create(descriptions, ignore_conflicts=True)

        if OrderNumber.objects.count() == 0:
            OrderNumber.objects.create(
                number=1,
                reset_date=jdatetime.date(1403, 7, 1),
            )

        self.stdout.write(self.style.SUCCESS('Price initialization completed successfully'))