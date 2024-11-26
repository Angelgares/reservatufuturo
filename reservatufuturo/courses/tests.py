from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Course
from home.models import Reservation


class CourseViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear grupo 'academy' para verificar permisos
        cls.academy_group = Group.objects.create(name='academy')

        # Crear usuario normal
        cls.user = User.objects.create_user(username='testuser', password='password')

        # Crear usuario con permisos de academy
        cls.academy_user = User.objects.create_user(username='academyuser', password='password')
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
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
        self.assertIn('course', response.context)

    # def test_add_to_cart_authenticated_user(self):
    #     self.client.login(username='testuser', password='password')
    #     response = self.client.post(reverse('add_to_cart', args=[self.course.id]))
    #     self.assertEqual(response.status_code, 302)  # Redirección al carrito
    #     reservation = Reservation.objects.get(user=self.user, course=self.course)
    #     self.assertTrue(reservation.cart)
    #     self.assertEqual(reservation.paymentMethod, 'Pending')

    def test_add_to_cart_unauthenticated_user(self):
        response = self.client.post(reverse('add_to_cart', args=[self.course.id]))
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
        response = self.client.post(reverse('delete_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_delete_course_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.post(reverse('delete_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)  # Redirección a lista de cursos
        self.assertFalse(Course.objects.filter(id=self.course.id).exists())

    def test_update_course_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('update_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_update_course_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.get(reverse('update_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/update_course.html')

    def test_course_inscriptions_permission_denied_for_normal_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('course_inscriptions', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_course_inscriptions_permission_allowed_for_academy_user(self):
        self.client.login(username='academyuser', password='password')
        response = self.client.get(reverse('course_inscriptions', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_inscriptions.html')
