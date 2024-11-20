from django.urls import path
from .views import CartView, remove_from_cart

app_name = 'cart'

urlpatterns = [
    path('cart', CartView.as_view(), name='cart'),
    path('remove/<int:reservation_id>/', remove_from_cart, name='remove_from_cart'),
]
