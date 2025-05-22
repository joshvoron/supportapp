from rest_framework import serializers


# GetChats serializers
class ChatSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    theme = serializers.CharField()
    last_msg = serializers.CharField()


class ChatListSerializer(serializers.Serializer):
    bot_name = serializers.CharField()
    chats = ChatSerializer(many=True)


# GetMessages serializer
class ChatMessagesInputSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField()
    message_id = serializers.UUIDField(required=False, allow_null=True)
    include_info = serializers.BooleanField(default=False)


class MessageOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField(source='user.id')
    user_type = serializers.CharField(source='user.type')
    text = serializers.CharField()
    sended = serializers.DateTimeField()


class ChatInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    client_name = serializers.CharField()
    created = serializers.DateTimeField()
    is_solved = serializers.BooleanField()
    theme = serializers.CharField()
    solved_by = serializers.UUIDField(allow_null=True)


class MessagesListSerializer(serializers.Serializer):
    chat_info = ChatInfoSerializer(required=False)
    messages = MessageOutputSerializer(many=True)
