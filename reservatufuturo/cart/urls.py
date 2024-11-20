from django.urls import path
from .views import CartView
from .services import remove_from_cart, add_to_cart, checkout

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('remove/<int:reservation_id>/', remove_from_cart, name='remove_from_cart'),
    path('add/<int:course_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', CartView.as_view(template_name='cart/payment_success.html'), name='payment_success'),
    path('cancel/', CartView.as_view(template_name='cart/payment_cancel.html'), name='payment_cancel'),
]

