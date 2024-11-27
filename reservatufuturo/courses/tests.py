from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Course
from home.models import Reservation
from django.contrib.auth.models import User
from home.models import Reservation
from courses.models import Course



class CourseViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear grupo 'academy' para verificar permisos
        cls.academy_group = Group.objects.create(name='academy')

        # Crear usuario normal
        cls.user = User.objects.create_user(
            username='testuser', password='password')

        # Crear usuario con permisos de academy
        cls.academy_user = User.objects.create_user(
            username='academyuser', password='password')
        cls.academy_user.groups.add(cls.academy_group)

        # Crear un curso de prueba
        cls.course = Course.objects.create(
            name='Test Course',
            teacher='Test Teacher',
            type='Magisterio',
            price=100.0,
            capacity=10,
            image='test_image.jpg',
            description='A sample test course description.',
            starting_date=date.today(),
            ending_date=date.today(),
        )

    def test_course_list_view(self):
        response = self.client.get(reverse('courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_list.html')
        self.assertIn('courses_grouped', response.context)

    def test_course_detail_view(self):
        response = self.client.get(
            reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
        self.assertIn('course', response.context)

    def test_add_to_cart_unauthenticated_user(self):
        response = self.client.post(
            reverse('add_to_cart', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirección al login

    def test_create_course_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_create_course_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/create_course.html')

    def test_delete_course_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(
            reverse('delete_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_update_course_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(
            reverse('update_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_update_course_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.get(
            reverse('update_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/update_course.html')

    def test_course_inscriptions_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(
            reverse('course_inscriptions', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_course_inscriptions_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.get(
            reverse('course_inscriptions', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_inscriptions.html')

    def test_create_course(self):
        Course.objects.create(
            name='New Test Course',
            teacher='New Test Teacher',
            type='Magisterio',
            price=150.0,
            capacity=20,
            description='New course description',
            starting_date=date.today(),
            ending_date=date.today(),
        )

        created_course = Course.objects.get(name='New Test Course')
        self.assertEqual(created_course.name, 'New Test Course')
        self.assertEqual(created_course.price, 150.0)

    def test_delete_course(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.post(
            reverse('delete_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())
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