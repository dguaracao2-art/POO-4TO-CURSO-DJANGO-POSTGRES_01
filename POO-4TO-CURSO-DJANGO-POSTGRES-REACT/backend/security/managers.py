from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Debe proporcionar un email válido")

    def create_user(self, username, first_name, last_name, email, password=None, **extra_fields):
        if not username:
            raise ValueError("El username es obligatorio")
        if not first_name:
            raise ValueError("El nombre es obligatorio")
        if not last_name:
            raise ValueError("El apellido es obligatorio")
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("El email es obligatorio")
        user = self.model(
            username=username, first_name=first_name, last_name=last_name,
            email=email, **extra_fields,
        )
        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, first_name, last_name, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")
        return self.create_user(username, first_name, last_name, email, password, **extra_fields)
