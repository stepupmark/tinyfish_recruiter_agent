#Django imports
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.timezone import datetime, get_current_timezone

#local imports
from authentication.models import CustomUserModel 

class AuthBackend(BaseBackend):
    """
    Custom authentication backend for Django that supports login via email or mobile number.

    This backend allows users to authenticate using either their email address or mobile number,
    in addition to enforcing business rules such as:
    - Account activation
    - Password presence
    - Blocked user prevention
    - Last login timestamp update

    Methods:
        - authenticate(): Custom logic to authenticate the user.
        - get_user(): Returns a User object by its ID.

    Usage:
        Add this backend to your Django settings:

            AUTHENTICATION_BACKENDS = [
                'django.contrib.auth.backends.ModelBackend',
                'core.authentication.AuthBackend',  # This class
            ]
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUserModel.objects.get(Q(email=username))
            if not user.password:
                raise ValidationError('Password need to be provided by the super admin.')
            if password:
                password_check = user.check_password(password)
                if not password_check:
                    raise Exception("Password didn't match.")
            if not user.is_active:
                raise ValidationError("This account is marked not active, Please contact admin.")
            # if user.is_blocked:
            #     raise ValidationError("This account has been blocked, Please contact admin.")
            # user.last_login = datetime.now(tz=get_current_timezone())
            user.last_login = datetime.now()
            user.save()
            return user
        except CustomUserModel.DoesNotExist as e:
            raise ValidationError("No User Found with the given email.")
        
    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        try:
            return CustomUserModel.objects.get(id=user_id)
        except CustomUserModel.DoesNotExist as e:
            raise ValidationError("No User Found with the given email.")