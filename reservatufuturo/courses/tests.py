from django.test import TestCase
from django.contrib.auth.models import User
from home.models import Reservation
from courses.models import Course

class CourseReservationTest(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password')
        # Crear un curso de prueba
        self.course = Course.objects.create(
            name="Curso de Prueba",
            price=100.00,
            type="Educación",
            capacity=10,
            starting_date="2021-01-01",
            ending_date="2021-01-31",
        )

    def test_user_can_reserve_course(self):
        # Autenticar al usuario
        self.client.login(username='testuser', password='password')

        # Crear una reserva
        reservation = Reservation.objects.create(
            course=self.course,
            user=self.user,
            paymentMethod="Cash",
            cart=False,
        )

        # Verificar que la reserva se ha creado correctamente
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.course, self.course)
        self.assertEqual(reservation.paymentMethod, "Cash")
        self.assertFalse(reservation.cart)
        
    def test_user_cant_reserve_full_course(self):
        # Autenticar al usuario
        self.client.login(username='testuser', password='password')

        # Llenar el curso
        for i in range(10):
            Reservation.objects.create(
                course=self.course,
                user=self.user,
                paymentMethod="Cash",
                cart=False,
            )

        # Intentar crear una reserva
        reservation = Reservation.objects.create(
            course=self.course,
            user=self.user,
            paymentMethod="Cash",
            cart=False,
        )

        # Verificar que la reserva no se ha creado
        self.assertEqual(Reservation.objects.count(), 10)
        self.assertNotEqual(reservation.user, self.user)
        self.assertNotEqual(reservation.course, self.course)
        self.assertNotEqual(reservation.paymentMethod, "Cash")
        self.assertNotEqual(reservation.cart, False)
