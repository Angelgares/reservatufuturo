from .models import Course
from django.core.exceptions import ObjectDoesNotExist

class CourseRepository:
    @staticmethod
    def create_course(name, price, image=None, teacher=None, capacity=0):
        """
        Crea un nuevo curso y lo guarda en la base de datos.
        """
        course = Course(
            name=name,
            price=price,
            image=image,
            teacher=teacher,
            capacity=capacity
        )
        course.save()
        return course

    @staticmethod
    def get_course_by_id(course_id):
        """
        Obtiene un curso por su ID. Lanza ObjectDoesNotExist si no se encuentra.
        """
        try:
            return Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def list_all_courses():
        """
        Devuelve todos los cursos.
        """
        return Course.objects.all()
