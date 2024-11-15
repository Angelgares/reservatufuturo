from django.contrib.auth.models import User
from django.db import models
from courses.models import Course  


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.IntegerField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
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