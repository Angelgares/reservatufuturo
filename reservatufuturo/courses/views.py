from django.shortcuts import render, redirect
from django.contrib import messages
from .services import create_course, list_courses
from .forms import CourseForm 
from django.views import generic
from .models import Course

class CourseListView(generic.ListView):
    modle = Course
    context_object_name = 'courses_list'
    queryset = Course.objects.all()
    
class CourseDetailView(generic.DetailView):
    model = Course
    context_object_name = 'course'
    template_name = 'courses/course_detail.html'