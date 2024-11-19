from django import forms
from .models import Monitor


class AddMonitorForm(forms.ModelForm):
    """
    Form for creating a new Monitor instance.
    """

    class Meta:
        model = Monitor
        fields = [
            'name',
            'protocol',
            'interval',
            'url',
            'method',
            'host',
            'port',
            'alert_threshold',
            'description',
        ]
        widgets = {
            'protocol': forms.ChoiceField(choices=Monitor.PROTOCOL_CHOICES),
            'interval': forms.ChoiceField(choices=Monitor.INTERVAL_CHOICES),
        }

    def clean(self):
        """
        Custom validation to ensure that relevant fields are provided
        based on the selected protocol.
        """
        cleaned_data = super().clean()
        protocol = cleaned_data.get('protocol')
        url = cleaned_data.get('url')
        method = cleaned_data.get('method')
        host = cleaned_data.get('host')
        port = cleaned_data.get('port')

        if protocol == 'HTTP':
            if not url:
                self.add_error('url', 'URL is required for HTTP protocol.')
            if not method:
                self.add_error('method', 'HTTP method is required for HTTP protocol.')
        elif protocol in ['TCP', 'UDP']:
            if not host:
                self.add_error('host', 'Host is required for TCP/UDP protocols.')
            if not port:
                self.add_error('port', 'Port is required for TCP/UDP protocols.')

        return cleaned_data
