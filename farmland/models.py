from django.db import models
from django_jalali.db import models as jmodels



class Farmer(models.Model):
    name = models.CharField("نام", max_length=100)
    code_melli = models.CharField("کد ملی", max_length=10, unique=True)
    notebook_number = models.CharField("شماره دفترچه", max_length=32, unique=True)
    address = models.CharField("آدرس", max_length=500, default="")
    phone = models.CharField("تلفن", max_length=11)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "مالک"
        verbose_name_plural = "مالک ها"

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField("نام", max_length=100, unique=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "منطقه"
        verbose_name_plural = "مناطق"

    def __str__(self):
        return self.name


class FarmlandType(models.Model):
    name = models.CharField("نام", max_length=100, unique=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "نوع مزرعه"
        verbose_name_plural = "نوع های مزرعه"

    def __str__(self):
        return self.name


class Farmland(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, verbose_name="مالک")
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, verbose_name="منطقه")
    name = models.CharField("نام", max_length=100, null=True, blank=True)
    type = models.ForeignKey(FarmlandType, on_delete=models.CASCADE, verbose_name="نوع")
    area = models.FloatField("مساحت (هکتار)", null=True, blank=True)
    tree_count = models.IntegerField("تعداد درخت", default=0)
    address = models.CharField("آدرس", max_length=500, default="")
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "مزرعه"
        verbose_name_plural = "مزرعه ها"

    def __str__(self):
        return self.name

