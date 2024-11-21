from django.urls import path
from .views import CartView, QuickPurchaseView
from .services import remove_from_cart, add_to_cart, checkout, payment_success, quick_payment_success

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('remove/<int:reservation_id>/', remove_from_cart, name='remove_from_cart'),
    path('add/<int:course_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', CartView.as_view(template_name='cart/payment_cancel.html'), name='payment_cancel'),
    path('quick/<int:course_id>/', QuickPurchaseView.as_view(), name='quick_purchase'),
    path('quick/success/', quick_payment_success, name='quick_success'),
    path('quick/cancel/', CartView.as_view(template_name='cart/quick_cancel.html'), name='quick_cancel'),

]

