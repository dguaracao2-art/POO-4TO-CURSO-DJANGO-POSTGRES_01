import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(_("usuario"), max_length=150, unique=True)
    first_name = models.CharField(_("nombres"), max_length=50)
    last_name = models.CharField(_("apellidos"), max_length=50)
    email = models.EmailField(_("correo electrónico"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    foto = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        verbose_name='Archive Photo',
        max_length=1024,
        blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("usuario")
        verbose_name_plural = _("usuarios")
        ordering = ("-date_joined",)

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
