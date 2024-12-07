from django import forms
from .models import Monitor


class AddMonitorForm(forms.ModelForm):
    """
    Form for creating a new Monitor instance.
    """

    method = forms.ChoiceField(
        choices=Monitor.METHOD_CHOICES,
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
        """
        Custom validation for HTTP monitoring
        """
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        method = cleaned_data.get('method')

        if not url:
            self.add_error('url', 'URL is required.')
        if not method:
            self.add_error('method', 'HTTP method is required.')

        return cleaned_data
