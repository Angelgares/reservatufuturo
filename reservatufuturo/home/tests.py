from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class HomeTests(TestCase):
    
    def setUp(self):
        # Crear un usuario para probar login
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            password='12345'
        )
    
    def test_homepage_view(self):
        """Test para la vista de la página de inicio"""
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/homepage.html')

    def test_login_view(self):
        """Test para la vista de login"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/login.html')

    def test_register_view(self):
        """Test para la vista de registro"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/register.html')

    def test_profile_view_authenticated(self):
        """Test para la vista del perfil (requiere autenticación)"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/profile.html')