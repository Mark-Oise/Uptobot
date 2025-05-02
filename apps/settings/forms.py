from django import forms
from allauth.account.forms import ChangePasswordForm


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