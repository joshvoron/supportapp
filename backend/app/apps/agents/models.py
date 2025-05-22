import datetime
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from apps.agents.manager import AgentManager
from apps.users.models import UserModel


class AgentModel(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=16, null=False, blank=False)
    surname = models.CharField(max_length=32, null=False, blank=False)
    is_email_valid = models.BooleanField(default=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    last_online = models.DateTimeField(default=None,
                                       null=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = "username"

    objects = AgentManager()

    REQUIRED_FIELDS = ["email", "name", "surname"]

    def save(self, *args, **kwargs):
        is_new = not AgentModel.objects.filter(pk=self.pk).exists()
        super().save(*args, **kwargs)
        if is_new:
            UserModel.objects.create(id=self.id, username=self.username,
                                     type="agent")


