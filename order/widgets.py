from django import forms
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe

class JalaliDatePickerWidget(TextInput):
    """
    Custom widget using JalaliDatePicker library from https://github.com/majidh1/JalaliDatePicker
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'jalali-datepicker',
            'placeholder': 'yyyy-mm-dd',
            'data-jdp': '',
            'readonly': 'readonly'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        return html
    
    class Media:
        css = {
            'all': (
                'https://unpkg.com/@majidh1/jalalidatepicker/dist/jalalidatepicker.min.css',
            )
        }
        js = (
            'https://unpkg.com/@majidh1/jalalidatepicker/dist/jalalidatepicker.min.js',
        )

class FarmlandAutocompleteWidget(forms.TextInput):
    """
    Custom widget for AJAX farmland autocomplete search
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'farmland-autocomplete',
            'placeholder': 'نام مزرعه را تایپ کنید...',
            'autocomplete': 'off'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        # Add hidden input for storing the selected farmland ID
        hidden_input = f'<input type="hidden" name="{name}_id" id="id_{name}_id" value="">'
        # Add suggestions container
        suggestions_div = f'<div id="farmland-suggestions" class="farmland-suggestions"></div>'
        return mark_safe(html + hidden_input + suggestions_div)
    
    class Media:
        css = {
            'all': (
                # We'll add CSS inline in the template for simplicity
            )
        }
        js = (
            # We'll add JS inline in the template for simplicity
        )
