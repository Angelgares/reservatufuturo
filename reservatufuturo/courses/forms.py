from django import forms
from .models import Course
from datetime import date


class CourseForm(forms.ModelForm):
    
    TYPE_CHOICES = [
        ('Administración', 'Administración'),
        ('Justicia', 'Justicia'),
        ('Educación', 'Educación'),
        ('Sanidad', 'Sanidad'),
        ('Policía', 'Policía'),
        ('Bomberos', 'Bomberos'),
        ('Prisiones', 'Prisiones'),
        ('Hacienda', 'Hacienda'),
        ('Inspector', 'Inspector'),
        ('Técnicos', 'Técnicos'),
        ('Informática', 'Informática'),
        ('Telecomunicaciones', 'Telecomunicaciones'),
        ('Tecnología', 'Tecnologías'),
    ]
    
    name = forms.CharField(required=True, label="Nombre del curso")
    price = forms.FloatField(required=True, label="Precio del curso", min_value=0)
    image = forms.ImageField(label='Imagen del curso', required=False)
    teacher = forms.CharField(max_length=100, label="Profesor")
    capacity = forms.IntegerField(label="Capacidad del curso", required=True, min_value=1)
    description = forms.CharField(
        label='Descripción del curso',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40})
    )
    starting_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de inicio"
    )
    ending_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de finalización"
    )
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        initial='Justicia',
        label="Categoría"
    )
    
    class Meta:
        model = Course
        fields = [
            'name',
            'price',
            'image',
            'teacher',
            'capacity',
            'description',
            'starting_date',
            'ending_date',
            'type',
        ]
        widgets = {
            'starting_date': forms.DateInput(attrs={'type': 'date'}),
            'ending_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        starting_date = cleaned_data.get('starting_date')
        ending_date = cleaned_data.get('ending_date')
        today = date.today()
        
        if starting_date:
            if starting_date < today:
                self.add_error('starting_date', 'La fecha de inicio no puede ser anterior a la fecha actual.')

        if starting_date and ending_date:
            if ending_date < starting_date:
                self.add_error('ending_date', 'La fecha de finalización debe ser igual o posterior a la fecha de inicio.')
        
        return cleaned_data