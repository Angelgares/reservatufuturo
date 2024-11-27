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
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='reservations'  # Relación inversa personalizada
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Usuarios registrados opcionales
    email = models.EmailField(null=True, blank=True)  # Email para usuarios anónimos
    paymentMethod = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='Pending')
    cart = models.BooleanField(default=True)
    management_fee = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0, 
        null=False, 
        blank=False, 
        verbose_name="Gastos de gestión"
    )
    
    def save(self, *args, **kwargs):
        # Calcular automáticamente los gastos de gestión
        if self.course.price > 150:
            self.management_fee = 0.0
        else:
            self.management_fee = 5.0
        super().save(*args, **kwargs)

    def __str__(self):
        user_display = self.user.username if self.user else self.email
        return f'{user_display} - {self.course.name}'

