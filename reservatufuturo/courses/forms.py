from django import forms
from .models import Course
from django.core.exceptions import ValidationError

class CourseForm(forms.Form):
    
    TYPE_CHOICES = [
        ('Admnistrición General', 'Administración General'),
        ('Justicia', 'Justicia'),
        ('Educación', 'Educación'),
        ('Sanidad', 'Sanidad'),
        ('Policía', 'Policía'),
        ('Bomberos', 'Bomberos'),
        ('Prisiones', 'Prisiones'),
        ('Hacienda', 'Hacienda'),
        ('Inspector de Trabajo', 'Inspector de Trabajo'),
        ('Técnicos de Ayuntamientos', 'Técnicos de Ayuntamientos'),
        ('Informática', 'Informática'),
        ('Telecomunicaciones', 'Telecomunicaciones'),
        ('Tecnología de la Información', 'Tecnologías de la Información'),
    ]
    
    def clean(self):
        cleaned_data = super().clean()
        starting_date = cleaned_data.get('starting_date')
        ending_date = cleaned_data.get('ending_date')
        
        if starting_date and ending_date and starting_date >= ending_date:
            raise ValidationError({
                'starting_date': 'La fecha de inicio debe ser anterior a la fecha de finalización.',
                'ending_date': 'La fecha de finalización debe ser posterior a la fecha de inicio.',
            })

        return cleaned_data
    
    name = forms.CharField(required=True, label = "Nombre del curso")
    price = forms.FloatField(required=True, label = "Precio del curso")
    image = forms.ImageField(label='Imagen del curso', required=False)
    teacher = forms.CharField(max_length=100, label = "Profesor")
    capacity = forms.IntegerField(label = "Capacidad del curso", required=True)
    description = forms.CharField(label='Descripcion del curso', required=False, widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))
    starting_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de inicio")
    ending_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de finalización")
    type = forms.ChoiceField(choices=TYPE_CHOICES, initial='Justicia', label = "Categoría ")
    
