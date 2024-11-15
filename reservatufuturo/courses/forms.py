from django import forms
from .models import Course

class CourseForm(forms.ModelForm):        
    
    class Meta:
        model = Course
        fields = ['name', 'price', 'image', 'teacher', 'capacity']
