from django.contrib.auth.models import User
from django.db import models
from courses.models import Course


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    def __str__(self):
        return f'{self.user.username} Profile'
    
class Reservation(models.Model):
    PAYMENT_METHODS = [
        ('Online', 'Online'),
        ('Cash', 'Cash'),
        ('Pending', 'Pending')
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Usuarios registrados opcionales
    email = models.EmailField(null=True, blank=True)  # Email para usuarios anónimos
    paymentMethod = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Pending')
    cart = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.course.name}'