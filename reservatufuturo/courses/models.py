from django.db import models
import os
from django.conf import settings

# Create your models here.

class Course(models.Model):
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



    
    name = models.CharField(max_length=100, help_text='Course name')
    price = models.FloatField(max_length=10, help_text='Course price')
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    teacher = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text='Maximum number of students')
    description = models.TextField()
    starting_date = models.DateField()
    ending_date = models.DateField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Magisterio')

    
    
    def __str__(self):
        return self.name
    
    @property
    def is_full(self):
        """Returns True if the course is full based on confirmed reservations."""
        confirmed_reservations = self.reservations.exclude(paymentMethod='Pending').count()
        return confirmed_reservations >= self.capacity
