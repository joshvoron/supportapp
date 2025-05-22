import uuid

from django.db import models


class UserModel(models.Model):
    TYPE_CHOICES = {
        'client': 'Client',
        'agent': 'Agent'
    }
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, unique=True)
    type = models.CharField(choices=TYPE_CHOICES)
