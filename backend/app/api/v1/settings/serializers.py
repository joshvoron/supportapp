from rest_framework import serializers


# GetInfo serializers
class GraphPointSerializer(serializers.Serializer):
    date = serializers.CharField()
    value = serializers.FloatField()


class InfoSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.UUIDField()


class StatsSerializer(serializers.Serializer):
    avg_rating = serializers.FloatField()
    highest_rate = serializers.IntegerField()
    lowest_rate = serializers.IntegerField()
    requests_per_month = serializers.IntegerField()
    rating_graph = GraphPointSerializer(many=True)
    requests_graph = GraphPointSerializer(many=True)


class StatsResponseSerializer(serializers.Serializer):
    info = InfoSerializer()
    stats = StatsSerializer()


# Agent serializers
class AgentInfoSerializer(InfoSerializer):
    last_online = serializers.DateTimeField(allow_null=True)


class AgentStatsSerializer(StatsSerializer):
    online_days = serializers.IntegerField()


class AgentStatsResponseSerializer(StatsResponseSerializer):
    info = AgentInfoSerializer()
    stats = AgentStatsSerializer()


# Bot serializers
class BotInfoSerializer(InfoSerializer):
    added = serializers.DateTimeField()
    security_key = serializers.UUIDField()


class BotStatsSerializer(StatsSerializer):
    most_active_agent = serializers.CharField()


class BotStatsResponseSerializer(StatsResponseSerializer):
    info = BotInfoSerializer()
    stats = BotStatsSerializer()


# Group serializers
class GroupInfoSerializer(InfoSerializer):
    created = serializers.DateTimeField()


class GroupStatsResponseSerializer(StatsResponseSerializer):
    info = GroupInfoSerializer()
    stats = BotStatsSerializer()


# GetObject serializers
class ObjectSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()

