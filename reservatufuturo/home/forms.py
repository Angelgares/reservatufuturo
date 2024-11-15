from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Apellidos",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Número de teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone_number", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()
        return user
    
class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Apellidos",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class ProfileUpdateForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Número de teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )
    class Meta:
        model = Profile
        fields = ['phone_number']