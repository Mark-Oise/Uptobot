from django import forms
from .models import Monitor
from .tasks import check_monitor


class AddMonitorForm(forms.ModelForm):
    """
    Form for creating a new Monitor instance.
    """

    class Meta:
        model = Monitor
        fields = [
            'name',
            'interval',
            'url',
            'description',
        ]

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        interval = cleaned_data.get('interval')

        if not url:
            self.add_error('url', 'URL is required.')
        if not interval or interval < 5 or interval > 60:
            self.add_error('interval', 'Interval must be between 5 and 60 minutes.')
        
        return cleaned_data

    def save(self, commit=True):
        monitor = super().save(commit=commit)
        if commit:
            # Trigger an immediate check
            check_monitor.delay(monitor.id)
        return monitor
    
    

class UpdateMonitorForm(forms.ModelForm):
    """
    Form for updating an existing Monitor instance.
    """
    alert_threshold = forms.IntegerField(
        min_value=5,
        max_value=60,
        required=True,
        widget=forms.NumberInput(attrs={'type': 'hidden'})
    )

    class Meta:
        model = Monitor
        fields = [
            'name',
            'interval',
            'url',
            'alert_threshold',
            'description',
        ]


    def save(self, commit=True):
        monitor = super().save(commit=commit)
        if commit:
            # Check if critical monitoring parameters have changed
            critical_fields = ['url', 'interval']
            if self.has_changed() and any(field in self.changed_data for field in critical_fields):
                # Trigger an immediate check
                check_monitor.delay(monitor.id)
        return monitor
