from django.urls import path
from .views import CartView
from .services import remove_from_cart, add_to_cart

app_name = 'cart'

urlpatterns = [
    path('cart', CartView.as_view(), name='cart'),
    path('remove/<int:reservation_id>/', remove_from_cart, name='remove_from_cart'),
    path('add/<int:course_id>/', add_to_cart, name='add_to_cart'),

]
