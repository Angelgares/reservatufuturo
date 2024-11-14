from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, label="Nombre de usuario")
    email = forms.EmailField(required=True)
    complete_name = forms.CharField(max_length=50, required=True, label="Nombre completo")
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ("username", "complete_name", "email", "phone_number", "password1", "password2")
