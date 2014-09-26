from django import forms


class loginForm(forms.Form):
    userName = forms.CharField(max_length=256)
    passKey = forms.CharField(widget=forms.PasswordInput())
