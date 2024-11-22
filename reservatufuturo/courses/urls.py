from django.contrib import admin
from django.urls import path, include
from courses import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("home.urls")),
    path("courses", views.CourseListView.as_view(), name="courses"),
    path("courses/<int:pk>", views.CourseDetailView.as_view(), name="course_detail"),
    path("courses/add_to_cart/<int:course_id>/", views.add_to_cart, name="add_to_cart"),
    path('courses/create', views.create_course, name='create_course'),
    path('courses/update/<int:pk>', views.update_course, name='update_course'),
    path('courses/delete/<int:pk>', views.delete_course, name='delete_course'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)