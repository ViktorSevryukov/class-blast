from django import forms


class EnrollLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class AHALoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)