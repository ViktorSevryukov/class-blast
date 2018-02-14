from django import forms
from apps.core.models import *

#
# class Login(forms.Form):
#     username = forms.CharField(label='username', max_length=100)

#TODO: passwordinput field type

class EnrollLoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class AHALoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)