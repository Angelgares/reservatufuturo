from django.urls import path
from . import views
from .views import CustomLoginView, register
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path('profile/', views.profile, name='profile'),
    path('editMyProfile/', views.edit_profile, name='edit_profile'),
    path('myCourses/', views.my_courses, name='my_courses'),
    path('aboutUs/', views.about_us, name='about_us'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)