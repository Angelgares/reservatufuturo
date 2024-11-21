from django.contrib import admin
from django.urls import path, include
from courses import views

urlpatterns = [
    path("", include("home.urls")),
    path("courses", views.CourseListView.as_view(), name="courses"),
    path("courses/<int:pk>", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/add_to_cart/<int:course_id>/", views.add_to_cart, name="add_to_cart"),
    path('courses/create', views.create_course, name='create_course'),
]
