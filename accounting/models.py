from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_jalali.db import models as jmodels


class Setting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    fa_name = models.CharField("نام", max_length=100)
    value = models.CharField("مقدار", )
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "تنظیمات"
        verbose_name_plural = "تنظیمات"

    def __str__(self):
        return self.name


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
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    amount = models.IntegerField("مقدار")
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"
    
    def save(self, *args, **kwargs):
        # The content_object handles the relationship automatically
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.content_object:
            # Handle both WaterOrder and GoodsOrder
            if hasattr(self.content_object, 'farmland'):  # WaterOrder
                return f"{self.content_object.farmland.name} - {self.amount}"
            elif hasattr(self.content_object, 'farmer'):  # GoodsOrder
                return f"{self.content_object.farmer.name} - {self.amount}"
            else:
                return f"{self.content_object} - {self.amount}"
        else:
            return f"Payment - {self.amount}"
