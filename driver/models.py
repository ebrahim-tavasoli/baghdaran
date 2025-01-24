from django.db import models
from django_jalali.db import models as jmodels

class Driver(models.Model):
    name = models.CharField("نام", max_length=255)
    phone = models.CharField("تلفن", max_length=11)
    car_number = models.CharField("شماره ماشین", max_length=16, unique=True)
    car_type = models.CharField("نوع ماشین", choices=[('pickup', 'وانت'), ('truck', 'کامیون')], max_length=16)
    capacity = models.IntegerField("حجم ماشین (لیتر)", default=10000)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = 'راننده'
        verbose_name_plural = 'رانندگان'

    def __str__(self):
        return self.name
