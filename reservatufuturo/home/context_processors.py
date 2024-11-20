from django.contrib.auth.models import Group

def user_group_context(request):
    return {
        'user_in_academy': (
            request.user.is_authenticated
            and request.user.groups.filter(name='academy').exists()
        )
    }
