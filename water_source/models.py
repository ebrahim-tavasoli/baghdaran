from django.db import models
from django_jalali.db import models as jmodels

class WaterSource(models.Model):
    name = models.CharField("نام", max_length=100, unique=True)
    operator = models.CharField("اپراتور", max_length=100)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = 'منبع آب'
        verbose_name_plural = 'منابع آب'

    def __str__(self):
        return self.name