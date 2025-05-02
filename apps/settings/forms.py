from django import forms
from allauth.account.forms import ChangePasswordForm
from apps.accounts.models import User



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



class CustomChangePasswordForm(ChangePasswordForm):
    oldpassword = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput()
    )
    password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput()
    )