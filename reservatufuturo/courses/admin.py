from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib import admin
from home.mail import enviar_notificacion_email
from django.conf import settings

class CustomUserAdmin(admin.ModelAdmin):
    # Configura los campos visibles en la lista del admin
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')

    def delete_model(self, request, obj):
        # Antes de eliminar al usuario, envía un correo
        destinatario = obj.email
        subject = "Eliminación de cuenta en ReservaTuFuturo"
        message = (
            f"Hola {obj.first_name},\n\n"
            "Lamentamos informarle que su cuenta ha sido eliminada de nuestra plataforma. "
            "Si crees que esto fue un error, por favor contáctanos."
            "Atentamente,\nEquipo de ReservaTuFuturo."
        )

        enviar_notificacion_email(destinatario, subject, message)

        # Llama al método padre para eliminar el usuario
        super().delete_model(request, obj)

# Desvincula el admin original del modelo User
admin.site.unregister(User)

# Vuelve a registrar el modelo User con el administrador personalizado
admin.site.register(User, CustomUserAdmin)

