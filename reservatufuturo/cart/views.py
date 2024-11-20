from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_list_or_404
from django.views import generic
from home.models import Reservation
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

class CartView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener las reservas del usuario actual que están en el carrito
        reservations = Reservation.objects.filter(user=self.request.user, cart=True)

        # Calcular el precio total
        total_price = sum(reservation.course.price for reservation in reservations)

        # Añadir al contexto
        context['reservations'] = reservations
        context['total_price'] = total_price

        return context
    
@login_required
def remove_from_cart(request, reservation_id):
    # Obtener la reserva por ID y asegurar que pertenece al usuario autenticado
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # Cambiar el estado del carrito a False (eliminar del carrito)
    reservation.cart = False
    reservation.save()

    # Redirigir al carrito
    return redirect('cart:cart')
