from django import forms
from allauth.account.forms import ChangePasswordForm
from .models import User, UserAlertSettings

class UserAccountUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class UserAlertSettingsForm(forms.ModelForm):
    class Meta:
        model = UserAlertSettings
        fields = [
            'email_alerts_enabled',
            'sms_alerts_enabled',
            'alert_frequency',
            'silent_hours_start',
            'silent_hours_end'
        ]
        widgets = {
            'silent_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'silent_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }


class CustomChangePasswordForm(ChangePasswordForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput()
    )


