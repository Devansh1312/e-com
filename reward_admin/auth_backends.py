from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MembershipIDBackend(ModelBackend):
    def authenticate(self, request, membership_id=None, password=None, **kwargs):
        try:
            user = User.objects.get(membership_id=membership_id)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
