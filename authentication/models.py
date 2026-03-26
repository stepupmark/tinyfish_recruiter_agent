from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.conf import settings
from datetime import datetime
from django.utils import timezone

import uuid
import pytz
from core.choice_fields import UserRoles, UserStatusChoices

# Create your models here.


class CommonModel(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,unique=True)
    is_active = models.BooleanField(default=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


    def created_time(self):
        if settings.USE_TZ:
            return self.created_at.astimezone(pytz.timezone(settings.TIME_ZONE))
        return self.created_at

    def last_updated(self):
        if settings.USE_TZ:
            return self.modified_at.astimezone(pytz.timezone(settings.TIME_ZONE))
        return self.modified_at
    
class CustomUserManager(BaseUserManager):
    def create_user(self,email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        extra_fields.setdefault("role", UserRoles.CANDIDATE)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, password, **extra_fields)
    



class CustomUserModel(AbstractBaseUser, CommonModel):
    full_name = models.CharField(max_length=200,null=True,blank=True)
    username = models.CharField(max_length=225,null=True,blank=True,unique=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15,null=True,unique=True)

    role = models.CharField(max_length=20,choices=UserRoles.choices,default=UserRoles.CANDIDATE)
    status = models.CharField(max_length=10,choices=UserStatusChoices.choices,default=UserStatusChoices.ACTIVE)

    is_staff = models.BooleanField(default=False)
    is_superuser =  models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name','password']

    objects = CustomUserManager()


    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['email','role'],name='unique_email_role')]

    def __str__(self):
        return f"{self.username}- {self.email} - {self.role}"
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    


