from django.db import models

# Create your models here.

class Course(models.Model):
    TYPE_CHOICES = [
        ('Admnistrición General', 'Administración General'),
        ('Justicia', 'Justicia'),
        ('Educación', 'Educación'),
        ('Sanidad', 'Sanidad'),
        ('Policía', 'Policía'),
        ('Bomberos', 'Bomberos'),
        ('Prisiones', 'Prisiones'),
        ('Hacienda', 'Hacienda'),
        ('Inspecto de Trabajo', 'Inspector de Trabajo'),
        ('Técnicos de Ayuntamientos', 'Técnicos de Ayuntamientos'),
        ('Informática', 'Informática'),
        ('Telecomunicaciones', 'Telecomunicaciones'),
        ('Tecnología de la Información', 'Tecnologías de la Información'),
    ]



    
    name = models.CharField(max_length=100, help_text='Course name')
    price = models.FloatField(max_length=10, help_text='Course price')
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    teacher = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text='Maximum number of students')
    description = models.TextField()
    starting_date = models.DateField()
    ending_date = models.DateField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Magisterio')
    
    
    def __str__(self):
        return self.name