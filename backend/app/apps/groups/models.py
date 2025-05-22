import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class GroupModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    owner = models.ForeignKey(to="agents.AgentModel",
                              on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=32, null=False, blank=False)
    bots = models.ManyToManyField('BotModel', related_name='groups')
    agents = models.ManyToManyField('agents.AgentModel', related_name='groups')


class BotModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=32, null=False, blank=False)
    last_online = models.DateTimeField(null=False, blank=False,
                                       default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    secret_key = models.UUIDField(default=uuid.uuid4, editable=False,
                                  unique=True)


class RequestModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    client = models.ForeignKey(to='clients.ClientModel',
                               on_delete=models.CASCADE)
    is_solved = models.BooleanField(default=False, null=False, blank=False)
    solved_by = models.ForeignKey(to="agents.AgentModel", null=True,
                                  blank=False, on_delete=models.CASCADE)
    theme = models.TextField(null=False, blank=False, default="Request")
    bot = models.ForeignKey(to='BotModel', on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator, MaxValueValidator],
        null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)


class MessageModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    text = models.TextField(null=False, blank=False)
    sended = models.DateTimeField(editable=False,
                                  auto_now_add=True)
    user = models.ForeignKey(to='users.UserModel', on_delete=models.CASCADE)
    request = models.ForeignKey(to='RequestModel', on_delete=models.CASCADE)
