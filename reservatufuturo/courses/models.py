from django.db import models

# Create your models here.

class Course(models.Model):
    TYPE_CHOICES = [
        ('INF', 'Informática'),
        ('BIO', 'Biología'),
        ('QUI', 'Química'),
        ('FIS', 'Física'),
        ('MAT', 'Matemáticas'),
        ('HIS', 'Historia'),
        ('ECO', 'Economía'),
        ('PSI', 'Psicología'),
        ('ART', 'Arte'),
        ('IDI', 'Idiomas'),
    ]

    
    name = models.CharField(max_length=100, help_text='Course name')
    price = models.FloatField(max_length=10, help_text='Course price')
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    teacher = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text='Maximum number of students')
    description = models.TextField()
    starting_date = models.DateField()
    ending_date = models.DateField()
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='Magisterio')
    
    
    def __str__(self):
        return self.name