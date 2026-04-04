from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        VIEWER  = "viewer",  "Viewer"
        ANALYST = "analyst", "Analyst"
        ADMIN   = "admin",   "Admin"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name"]
 
    class Meta:
        ordering = ["id"]
 
    def __str__(self):
        return f"{self.name} - [{self.role}]"
 
    def is_viewer(self):
        return self.role == self.Role.VIEWER
 
    def is_analyst(self):
        return self.role == self.Role.ANALYST
 
    def is_admin_role(self):
        return self.role == self.Role.ADMIN