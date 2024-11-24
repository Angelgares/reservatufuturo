from django.urls import path
from .views import CartView, QuickPurchaseView, QuickCashPurchaseView
from .services import remove_from_cart, add_to_cart, checkout, payment_success, quick_payment_success, payment_cancel, cash, cash_success

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('remove/<int:reservation_id>/', remove_from_cart, name='remove_from_cart'),
    path('add/<int:course_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('cash/', cash, name='cash'),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
    path('quick/<int:course_id>/', QuickPurchaseView.as_view(), name='quick_purchase'),
    path('quick/success/', quick_payment_success, name='quick_success'),
    path('cash/success', cash_success, name='cash_success'),
    path('quick/cancel/', payment_cancel, name='quick_cancel'),
    path('quick/cash/<int:course_id>/', QuickCashPurchaseView.as_view(), name='cash_purchase'),
]

