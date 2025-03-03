from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

class EcoUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

USER_ROLES = [
    ('admin', 'Admin'),
    ('trader', 'Trader'),
    ('shipping', 'Shipping'),
]

class EcoUser(AbstractBaseUser, PermissionsMixin):

    admin='Admin'
    trader='Trader'
    shipping='Shipping'

    username = models.CharField(max_length=150, blank=True, null=True)  # Add username fieldver
    email = models.EmailField(unique=True)  # Use email as the username
    role = models.CharField(max_length=20, choices=USER_ROLES)
    password = models.CharField(max_length=128, default="fuckyou")  # Add password field
    first_name = models.CharField(max_length=30, blank=True, null=True)  # Add first_name field
    last_name = models.CharField(max_length=30, blank=True, null=True)  # Add last_name field

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EcoUserManager()

    groups = models.ManyToManyField(
        Group,
        related_name="eco_user_groups",  # Change related_name to avoid conflict
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="eco_user_permissions",  # Change related_name to avoid conflict
        blank=True
    )

    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = []  # No other required fields

    def __str__(self):
        return f"{self.email} ({self.role})"
