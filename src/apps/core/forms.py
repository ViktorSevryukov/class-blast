from django import forms


class EnrollLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50,
                               widget=forms.TextInput(
                                   attrs={'id': 'enroll_username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'enroll_password'}))


class AHALoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50,
                               widget=forms.TextInput(
                                   attrs={'id': 'aha_username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'aha_password'}))
