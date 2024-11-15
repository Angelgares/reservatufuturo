from django.db import models

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=100, help_text='Course name')
    price = models.FloatField(max_length=10, help_text='Course price')
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    teacher = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text='Maximum number of students')
    
    def __str__(self):
        return self.name