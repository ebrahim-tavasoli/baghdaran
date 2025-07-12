from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericInlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.contrib.contenttypes.admin import BaseGenericInlineFormSet
from accounting import models


class PaymentInlineFormSet(BaseGenericInlineFormSet):
    def save_new(self, form, commit=True):
        """Override to ensure proper saving - the content_object is set automatically"""
        payment = super().save_new(form, commit=commit)
        return payment
    
    def save_existing(self, form, instance, commit=True):
        """Override to ensure proper saving - the content_object is set automatically"""
        payment = super().save_existing(form, instance, commit=commit)
        return payment


class PaymentInline(GenericTabularInline):
    model = models.Payment
    formset = PaymentInlineFormSet
    extra = 1
    fields = ('amount', 'created_at')
    readonly_fields = ('created_at',)
    
    def get_fields(self, request, obj=None):
        # Hide the content_type and object_id fields in the inline
        # They will be automatically set by the formset
        return self.fields


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'amount', 'created_at')
    list_filter = ('created_at', 'content_type')
    search_fields = ('amount',)
    readonly_fields = ('created_at', 'updated_at')
    fields = ('content_type', 'object_id', 'amount', 'created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        # Make GenericForeignKey fields read-only when editing existing payments
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(['content_type', 'object_id'])
        return readonly
    
    def content_object(self, obj):
        """Display better representation of the related object"""
        if obj.content_object:
            if hasattr(obj.content_object, 'farmland'):  # WaterOrder
                return f"حواله آب - {obj.content_object.farmland.name}"
            elif hasattr(obj.content_object, 'farmer'):  # GoodsOrder
                return f"حواله کالا - {obj.content_object.farmer.name}"
            else:
                return str(obj.content_object)
        return "-"
    
    content_object.short_description = "شی مرتبط"


@admin.register(models.Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ("fa_name", "value")
    search_fields = ("name", "fa_name")
    readonly_fields = ("updated_at", "fa_name")
    ordering = ("-updated_at",)
    exclude = ('name',)


@admin.register(models.Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ("fa_name", "value")
    search_fields = ("name", "fa_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)
    