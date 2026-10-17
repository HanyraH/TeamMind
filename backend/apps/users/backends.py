"""Authentication backend supporting login with email or username."""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if not username or not password:
            return None

        try:
            user = User.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).order_by('id').first()
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
