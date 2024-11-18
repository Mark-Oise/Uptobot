from django import forms
from .models import Monitor
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re


class AddMonitorForm(forms.ModelForm):
    def clean_url(self):
        url = self.cleaned_data.get('url')
        protocol = self.cleaned_data.get('protocol', 'HTTP')

        if protocol == 'HTTP':
            # Validate HTTP URLs
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise ValidationError('Please enter a valid HTTP URL')
        else:
            # For TCP/UDP, validate host:port format
            pattern = r'^[\w.-]+:\d{1,5}$'
            if not re.match(pattern, url):
                raise ValidationError('For TCP/UDP, use format host:port (e.g., example.com:8080)')
            
            # Validate port range
            try:
                port = int(url.split(':')[1])
                if port < 1 or port > 65535:
                    raise ValidationError('Port must be between 1 and 65535')
            except (IndexError, ValueError):
                raise ValidationError('Invalid port number')

        return url

    def clean(self):
        cleaned_data = super().clean()
        interval = cleaned_data.get('interval')
        custom_interval = cleaned_data.get('custom_interval')

        # Validate custom interval if selected
        if interval == 'custom':
            if not custom_interval:
                raise ValidationError({
                    'custom_interval': 'Custom interval is required when custom is selected'
                })
            if custom_interval < 1:
                raise ValidationError({
                    'custom_interval': 'Custom interval must be at least 1 minute'
                })
            if custom_interval > 1440:  # 24 hours in minutes
                raise ValidationError({
                    'custom_interval': 'Custom interval cannot exceed 24 hours (1440 minutes)'
                })
        elif custom_interval:
            # Clear custom_interval if not using custom
            cleaned_data['custom_interval'] = None

        return cleaned_data

    class Meta:
        model = Monitor
        fields = [
            'url',
            'protocol',
            'interval',
            'custom_interval',
            'alert_threshold',
            'is_online'
        ]
        widgets = {
            'url': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'For HTTP: https://example.com, For TCP/UDP: host:port'
            }),
            'custom_interval': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter interval in minutes'
            }),
            'alert_threshold': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'max': '10'
            })
        }
        help_texts = {
            'url': 'For HTTP monitors, enter full URL. For TCP/UDP, enter host:port',
            'alert_threshold': 'Number of consecutive failures before alert is triggered (1-10)',
        }
