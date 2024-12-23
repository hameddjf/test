from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):

        if not email:
            raise ValueError()
        if not username:
            raise ValueError()

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('مدیر باید حتماً دارای is_staff=True باشد.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                _('مدیر باید حتماً دارای is_superuser=True باشد.'))

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=16, default=None, blank=True, null=True)
    last_name = models.CharField(
        max_length=16, default=None, blank=True, null=True)
    email = models.EmailField(_('ایمیل'), unique=True)
    username = models.CharField(_('نام کاربری'), unique=True, max_length=25)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
