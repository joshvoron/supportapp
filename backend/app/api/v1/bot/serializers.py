from rest_framework import serializers


class CreateRequestInputSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    name = serializers.CharField()
    theme = serializers.CharField()


class CreateRequestOutputSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    chat_id = serializers.UUIDField()
