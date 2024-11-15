from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Course(models.Model):
    name = models.CharField(max_length=100, help_text='Course name')
    price = models.FloatField(max_length=10, help_text='Course price')
    image = models.ImageField(upload_to='course_images', null=True, blank=True)
    teacher = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text='Maximum number of students')
    
    def __str__(self):
        return self.name
    
class Reservation(models.Model):
    PAYMENT_METHODS = [
        ('Online', 'Online'),
        ('Cash', 'Cash'),
        ('Pending', 'Pending')
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paymentMethod = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Online')
    
    def __str__(self):
        return f'{self.user.username} - {self.course.name}'