from django.db import models
from django_jalali.db import models as jmodels


class Price(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fa_name = models.CharField("نام", max_length=100)
    value = models.IntegerField("مقدار")
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "قیمت"
        verbose_name_plural = "قیمت ها"

    def __str__(self):
        return self.name


class Payment(models.Model):
    order = models.ForeignKey('order.WaterOrder', on_delete=models.CASCADE, verbose_name="حواله", related_name="order_payments")
    amount = models.IntegerField("مقدار")
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"
    
    def __str__(self):
        return f"{self.order.farmland.name} - {self.amount}"
