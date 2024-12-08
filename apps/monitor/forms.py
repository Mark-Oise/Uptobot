from django import forms
from .models import Monitor


class AddMonitorForm(forms.ModelForm):
    """
    Form for creating a new Monitor instance.
    """
    method = forms.ChoiceField(
        choices=Monitor.METHOD_CHOICES,
    )
    
    alert_threshold = forms.IntegerField(
        min_value=5,
        max_value=60,
        initial=60,
        required=True,
        widget=forms.NumberInput(attrs={'type': 'hidden'})  # We'll use the range input in the template
    )

    class Meta:
        model = Monitor
        fields = [
            'name',
            'interval',
            'url',
            'method',
            'alert_threshold',
            'description',
        ]

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        method = cleaned_data.get('method')
        alert_threshold = cleaned_data.get('alert_threshold')
        interval = cleaned_data.get('interval')

        if not url:
            self.add_error('url', 'URL is required.')
        if not method:
            self.add_error('method', 'HTTP method is required.')
        if not interval or interval < 5 or interval > 60:
            self.add_error('interval', 'Interval must be between 5 and 60 minutes.')
        if alert_threshold is not None:
            if alert_threshold < 5 or alert_threshold > 60:
                self.add_error('alert_threshold', 'Alert threshold must be between 5 and 60 seconds.')

        return cleaned_data
