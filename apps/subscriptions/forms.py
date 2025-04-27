from django import forms
from .models import CancellationReason

class CancellationForm(forms.ModelForm):
    class Meta:
        model = CancellationReason
        fields = ['reason', 'feedback']

    def __init__(self, subscription=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription = subscription

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.subscription = self.subscription
        if commit:
            instance.save()
        return instance