from django.db import models
import uuid

from apps.users.models import UserModel


# Create your models here.
class ClientModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=False, null=False)
    telegram_id = models.CharField(max_length=32, blank=False, null=False,
                                   unique=True)

    def save(self, *args, **kwargs):
        is_new = not ClientModel.objects.filter(pk=self.pk).exists()
        super().save(*args, **kwargs)
        if is_new:
            UserModel.objects.create(id=self.id, username=self.telegram_id,
                                     type="client")
