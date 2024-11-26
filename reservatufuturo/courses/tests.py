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
        
    def test_user_can_add_course_to_cart(self):
        # Autenticar al usuario
        self.client.login(username='testuser', password='password')

        # Añadir el curso al carrito
        response = self.client.post(f'/cart/add/{self.course.id}/')

        # Verificar que el curso se ha añadido al carrito
        self.assertEqual(Reservation.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.course, self.course)
        self.assertEqual(reservation.paymentMethod, "Pending")
        self.assertTrue(reservation.cart)
        
    def test_user_can_remove_course_from_cart(self):
        # Autenticar al usuario
        self.client.login(username='testuser', password='password')

        # Añadir el curso al carrito
        self.client.post(f'/cart/add/{self.course.id}/')
        
        # Verificar que el curso se ha añadido al carrito
        self.assertEqual(Reservation.objects.count(), 1)

        # Eliminar el curso del carrito
        response = self.client.post(f'/cart/remove/{Reservation.objects.first().id}/')

        # Verificar que el curso se ha eliminado del carrito
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertRedirects(response, '/cart/')

    