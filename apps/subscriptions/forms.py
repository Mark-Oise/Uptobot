from django import forms
from .models import CancellationReason

class CancellationForm(forms.ModelForm):
    class Meta:
        model = CancellationReason
        fields = ['reason', 'feedback']