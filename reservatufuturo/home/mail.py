from django.core.mail import send_mail
from django.conf import settings

def enviar_notificacion_email(destinatario, asunto, mensaje):
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [destinatario],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")
