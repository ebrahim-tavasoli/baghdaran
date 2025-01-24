
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_jalali.db import models as jmodels
import random
from datetime import timedelta

from farmland.models import Farmer, Zone, Farmland, FarmlandType
from driver.models import Driver
from water_source.models import WaterSource
from order.models import WaterOrder
from accounting.models import Payment

class Command(BaseCommand):
    help = 'Generate sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating sample data...')

        # Create sample zones
        zones = []
        zone_names = ['شمال', 'جنوب', 'شرق', 'غرب', 'مرکز']
        for name in zone_names:
            zone = Zone.objects.create(name=name)
            zones.append(zone)

        # Create sample farmers
        farmers = []
        for i in range(20):
            farmer = Farmer.objects.create(
                name=f'کشاورز {i+1}',
                code_melli=f'{random.randint(1000000000, 9999999999)}',
                notebook_number=f'{random.randint(1000000000, 9999999999)}',
                phone=f'09{random.randint(100000000, 999999999)}',
                address=f'آدرس نمونه {i+1}'
            )
            farmers.append(farmer)

        # Create sample farmland types
        farmland_types = []
        for i in range(5):
            farmland_type = FarmlandType.objects.create(
                name=f'نوع مزرعه {i+1}'
            )
            farmland_types.append(farmland_type)

        # Create sample farmlands
        farmlands = []
        for i in range(30):
            farmland = Farmland.objects.create(
                name=f'مزرعه {i+1}',
                farmer=random.choice(farmers),
                zone=random.choice(zones),
                address=f'آدرس مزرعه {i+1}',
                type=random.choice(farmland_types),
                area=random.randint(1, 100),
                tree_count=random.randint(1, 1000)
            )
            farmlands.append(farmland)

        # Create sample drivers
        drivers = []
        for i in range(10):
            driver = Driver.objects.create(
                name=f'راننده {i+1}',
                car_number=f'{random.randint(1000000000, 9999999999)}',
                phone=f'09{random.randint(100000000, 999999999)}',
                car_type=random.choice(['pickup', 'truck']),
                capacity=random.choice([10000, 20000, 30000, 40000, 50000])
            )
            drivers.append(driver)

        # Create sample water sources
        water_sources = []
        for i in range(5):
            water_source = WaterSource.objects.create(
                name=f'منبع آب {i+1}',
            )
            water_sources.append(water_source)

        # # Create sample water orders
        # orders = []
        # for i in range(50):
        #     water_source_type = random.choice(['liter', 'time'])
        #     pipe_length_price_type = random.choice(['free', 'fix', 'dynamic'])
            
        #     order = WaterOrder.objects.create(
        #         farmland=random.choice(farmlands),
        #         driver=random.choice(drivers),
        #         water_source=random.choice(water_sources),
        #         water_source_type=water_source_type,
        #         amount=random.randint(1000, 10000) if water_source_type == 'liter' else random.randint(1, 24),
        #         pump_count=random.randint(0, 5),
        #         pipe_length_price_type=pipe_length_price_type,
        #         pipe_length=random.randint(1, 10) if pipe_length_price_type != 'free' else 0,
        #         valid_date=jmodels.jdatetime.date.today() + timedelta(days=random.randint(1, 30))
        #     )
        #     orders.append(order)

        #     # Create sample payments for each order
        #     total_price = order.total_price
        #     paid_amount = 0
        #     while paid_amount < total_price:
        #         payment_amount = min(
        #             random.randint(100000, 1000000),
        #             total_price - paid_amount
        #         )
        #         Payment.objects.create(
        #             water_order=order,
        #             amount=payment_amount
        #         )
        #         paid_amount += payment_amount

        self.stdout.write(self.style.SUCCESS('Sample data generated successfully'))
