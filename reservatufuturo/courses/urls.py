from django.contrib import admin
from django.urls import path, include
from courses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('courses', views.CourseListView.as_view(), name='courses'),
    path('courses/<int:pk>', views.CourseDetailView.as_view(), name='course_detail'),
]