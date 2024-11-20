from django.shortcuts import render
from django.views import generic

class CartView(generic.TemplateView):
    template_name = 'cart/cart.html'