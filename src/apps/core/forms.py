from django import forms


class EnrollLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50,
                               widget=forms.TextInput(
                                   attrs={'id': 'enroll_username',
                                          'class': 'credential_input'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'id': 'enroll_password', 'class': 'credential_input'}))


class AHALoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50,
                               widget=forms.TextInput(
                                   attrs={'id': 'aha_username',
                                          'class': 'credential_input'}))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'id': 'aha_password', 'class': 'credential_input'}))
