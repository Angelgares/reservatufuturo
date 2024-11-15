from .repositories import CourseRepository
from django.core.exceptions import ValidationError

def create_course(name, price, image=None, teacher=None, capacity=0):
    """
    Servicio para crear un curso usando el repositorio.
    """
    if capacity <= 0:
        raise ValidationError("La capacidad debe ser mayor a cero.")
    if price < 0:
        raise ValidationError("El precio no puede ser negativo.")
    
    # Usar el repositorio para crear el curso
    course = CourseRepository.create_course(
        name=name,
        price=price,
        image=image,
        teacher=teacher,
        capacity=capacity
    )
    return course

def list_courses():
    """
    Servicio para listar todos los cursos.
    """
    return CourseRepository.list_all_courses()
