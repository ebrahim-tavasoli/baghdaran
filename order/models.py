import jdatetime
from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models, transaction
from django.db.models import F
from django.dispatch import receiver
from django_jalali.db import models as jmodels
from tinymce.models import HTMLField

from accounting import models as accounting_models


class OrderNumber(models.Model):
    number = models.BigIntegerField(default=0)
    reset_date = jmodels.jDateField(auto_now_add=True)


class OrderDescription(models.Model):
    name = models.CharField(max_length=255, unique=True)
    fa_name = models.CharField("نام", max_length=255, unique=True)
    template = HTMLField("قالب", default="")
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)

    # water_order_liter
    # water_order_pipe

    class Meta:
        verbose_name = "توضیحات حواله"
        verbose_name_plural = "توضیحات حواله"

    def __str__(self):
        return self.fa_name


class WaterOrder(models.Model):
    number = models.BigIntegerField("شماره", default=0)
    farmland = models.ForeignKey("farmland.Farmland", on_delete=models.CASCADE, verbose_name="مزرعه")
    driver = models.ForeignKey("driver.Driver", on_delete=models.CASCADE, verbose_name="راننده")
    water_source = models.ForeignKey("water_source.WaterSource", on_delete=models.CASCADE, verbose_name="منبع آب")
    water_source_type = models.CharField("واحد مقدار آب", max_length=16, choices=[("liter", "لیتر"), (
        "time", "ساعت")])  # liter = tanker must transport, time = water transfer by pipes
    amount = models.IntegerField("مقدار آب", default=0)
    pump_count = models.IntegerField("پمپاژ محدد", default=0)
    pipe_length_price_type = models.CharField("نوع هزینه لوله", max_length=16, default="fix",
                                              choices=[("free", "رایگان"), ("fix", "ثابت"), ("dynamic", "متغیر")])
    pipe_length = models.IntegerField("طول لوله (کیلومتر)", default=0)
    valid_date = jmodels.jDateField("تاریخ اعتبار")
    water_price_base = models.IntegerField("قیمت پایه آب", default=0)
    pipe_price_base = models.IntegerField("قیمت پایه لوله", default=0)
    pump_price_base = models.IntegerField("قیمت پایه پمپاژ", default=0)
    total_price = models.IntegerField("مبلغ کل", default=0)
    created_date_at = jmodels.jDateField("تاریخ ایجاد", auto_now_add=True)
    created_time_at = models.TimeField("ساعت ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)
    payments = GenericRelation('accounting.Payment')

    class Meta:
        verbose_name = "حواله آب"
        verbose_name_plural = "حواله های آب"

    def __str__(self):
        return f"{self.farmland.name}"

    @property
    def valid_days(self):
        return (self.valid_date - self.created_date_at).days

    @property
    def tanker_count(self):
        if self.water_source_type == "liter":
            return self.amount // self.driver.capacity
        else:
            return None

    @property
    def pipe_price(self):
        if self.pipe_length_price_type == "fix":
            return self.pipe_price_base
        elif self.pipe_length_price_type == "dynamic":
            return (self.pipe_length * 1000 // 5) * self.amount * self.pipe_price_base
        else:
            return 0

    @property
    def water_price(self):
        return self.amount * self.water_price_base

    @property
    def pump_price(self):
        return self.pump_count * self.amount * self.pump_price_base

    @property
    def total_payment(self):
        try:
            return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        except:
            return 0

    @property
    def remaining_payment(self):
        try:
            return self.total_price - self.total_payment
        except:
            return 0

    valid_days.fget.short_description = "تعداد روزهای معتبر"
    tanker_count.fget.short_description = "تعداد تانکر"
    pipe_price.fget.short_description = "هزینه لوله"
    water_price.fget.short_description = "هزینه آب"
    pump_price.fget.short_description = "هزینه پمپاژ"
    total_payment.fget.short_description = "مبلغ پرداخت شده"
    remaining_payment.fget.short_description = "مانده حساب"


class GoodsItem(models.Model):
    name = models.CharField('نام', max_length=255, unique=True)
    code = models.CharField('کد کالا', max_length=255, unique=True)
    unit = models.CharField(
        'واحد',
        max_length=16,
        choices=[
            ('number', 'عدد'),
            ('kilogram', 'کیلوگرم'),
        ]
    )
    price = models.BigIntegerField('قیمت')
    created_at = jmodels.jDateTimeField('زمان ایجاد', auto_now_add=True)
    updated_at = jmodels.jDateTimeField('زمان به روز رسانی', auto_now=True)

    class Meta:
        verbose_name = "نهاده"
        verbose_name_plural = "نهاده ها"

    def __str__(self):
        return f"{self.code}-{self.name}"


class GoodsOrder(models.Model):
    number = models.BigIntegerField("شماره", default=0)
    farmer = models.ForeignKey('farmland.Farmer', on_delete=models.CASCADE, verbose_name='کشاورز')
    description = HTMLField('توضیحات', null=True, blank=True)
    discount_type = models.CharField(
        'نوع تخفیف',
        max_length=8,
        choices=(
            ("fix", "ثابت"),
            ("percent", "درصد")
        ),
        default="fix"
    )
    discount = models.DecimalField('میزان تخفیف', default=0, decimal_places=3, max_digits=15)
    tax = models.BooleanField('مالیات', default=False)
    total_price = models.IntegerField("مبلغ نهایی", default=0)
    created_date_at = jmodels.jDateField("تاریخ ایجاد", auto_now_add=True)
    created_time_at = models.TimeField("ساعت ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ بروزرسانی", auto_now=True)
    payments = GenericRelation('accounting.Payment')

    class Meta:
        verbose_name = "حواله نهاده"
        verbose_name_plural = "حواله های نهاده"

    def __str__(self):
        return f"{self.farmer.name}"

    @property
    def total_price_without_discount(self):
        price = 0
        for item in self.goods_order_goods_order_item.all():
            price += item.price
        return int(price)

    @property
    def total_price_with_discount(self):
        price = 0
        for item in self.goods_order_goods_order_item.all():
            price += item.price_with_discount

        if self.discount_type == "fix":
            return int(price - self.discount)
        elif self.discount_type == "percent":
            return int(price - price * (self.discount / Decimal(100.0)))

    @property
    def total_price_with_tax(self):
        if self.tax:
            return int(self.total_price_with_discount + self.total_price_with_discount * Decimal(0.1))
        return int(self.total_price_with_discount)

    @property
    def total_payment(self):
        try:
            return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        except:
            return 0

    @property
    def remaining_payment(self):
        try:
            return self.total_price - self.total_payment
        except:
            return 0

    total_price_without_discount.fget.short_description = 'قیمت کل بدون تخفیف'
    total_price_with_discount.fget.short_description = 'قیمت کل با تخفیف'
    total_price_with_tax.fget.short_description = 'قیمت کل با محاسبه ی مالیات'
    total_payment.fget.short_description = "مبلغ پرداخت شده"
    remaining_payment.fget.short_description = "مانده حساب"

class GoodsOrderItem(models.Model):
    goods_order = models.ForeignKey(
        GoodsOrder,
        on_delete=models.CASCADE,
        related_name='goods_order_goods_order_item',
        verbose_name='حواله کالا'
    )
    item = models.ForeignKey(GoodsItem, on_delete=models.CASCADE, verbose_name='کالا',
                             related_name='item_goods_order_item')
    quantity = models.IntegerField('مقدار', default=1)
    unit_price = models.BigIntegerField('قیمت واحد', default=0)
    created_at = jmodels.jDateTimeField('زمان ایجاد', auto_now_add=True)
    updated_at = jmodels.jDateTimeField('زمان به روز رسانی', auto_now=True)
    discount_type = models.CharField(
        'نوع تخفیف',
        max_length=8,
        choices=(
            ("fix", "ثابت"),
            ("percent", "درصد")
        ),
        default="fix"
    )
    discount = models.DecimalField('میزان تخفیف', default=0, decimal_places=3, max_digits=15)

    class Meta:
        verbose_name = "قلم حواله نهاده"
        verbose_name_plural = "اقلام حواله های نهاده"

    def __str__(self):
        return f"{self.goods_order.id}"

    @property
    def price(self):
        return int(self.quantity * self.unit_price)

    @property
    def price_with_discount(self):
        if self.discount_type == "fix":
            return int(self.price - self.discount)
        elif self.discount_type == "percent":
            return int(self.price - self.price * (self.discount / Decimal(100.0)))


@receiver(models.signals.post_save, sender=WaterOrder)
def fill_prices_water_order(sender, instance, created, **kwargs):
    from accounting.models import Price

    if created:
        if instance.water_source_type == "liter":
            water_price = Price.objects.get(name='water_price_liter').value
            pipe_price = 0
            pump_price = 0
        elif instance.water_source_type == "time":
            water_price = Price.objects.get(name='water_price_time').value

            if instance.pipe_length_price_type == "fix":
                pipe_price = Price.objects.get(name='pipe_price_fix').value
            elif instance.pipe_length_price_type == "dynamic":
                pipe_price = Price.objects.get(name='pipe_price_dynamic').value
            else:
                pipe_price = 0

            pump_price = Price.objects.get(name='pump_price').value

        instance.water_price_base = water_price
        instance.pipe_price_base = pipe_price
        instance.pump_price_base = pump_price

        instance.save()

        instance.total_price = instance.water_price + instance.pipe_price + instance.pump_price
        instance.save()


@receiver(models.signals.post_save, sender=WaterOrder)
def set_order_number_water_order(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            OrderNumber.objects.update(number=F("number") + 1)
            number = OrderNumber.objects.first().number
        instance.number = number
        instance.save()


@receiver(models.signals.pre_save, sender=OrderNumber)
def reset_order_number(sender, instance, **kwargs):
    new_reset_date = jdatetime.date(instance.reset_date.year + 1, 7, 1)
    today = jdatetime.datetime.today()
    if today >= new_reset_date:
        instance.number = 0
        instance.reset_date = today
        instance.save()

@receiver(models.signals.post_save, sender=GoodsOrderItem)
def fill_prices_goods_order(sender, instance, created, **kwargs):
    if created:
        instance.unit_price = instance.item.price
        instance.total_price = instance.total_price_with_tax
        instance.save()

@receiver(models.signals.post_save, sender=GoodsOrder)
def set_order_number_goods_order(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            OrderNumber.objects.update(number=F("number") + 1)
            number = OrderNumber.objects.first().number
        instance.number = number
        instance.save()