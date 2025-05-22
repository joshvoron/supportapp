import uuid

from django.db.models.functions import TruncDay, TruncDate
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Min, Max, Count
from rest_framework.permissions import IsAuthenticated

from apps.groups.models import RequestModel, BotModel, GroupModel
from apps.agents.models import AgentModel
import api.v1.settings.serializers as local_serializers


# Get stats
class StatsView(GenericAPIView):
    """
    Base class for any stats
    """
    model = None
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):
        """
        Recieving object (Group, Agent или Bot), return stats.
        in extra_info var you can add extra fields for info dict.
        in extra_stats var you can add extra fields for stats dict.
        """
        obj_id = request.data.get("id")
        if not obj_id:
            return Response({'error': 'Invalid or missing id'},
                            status=400)

        try:
            obj = self.model.objects.get(id=obj_id)
        except self.model.DoesNotExist:
            return Response({'error': "Model doesn't exist"},
                            status=400)

        qs = self.get_queryset_for_obj(obj)
        extra_info = self.get_extra_info(obj, qs)
        # Info part
        info = {
            "name": obj.name,
            "id": obj.id,
            **extra_info
        }
        # Stats part
        now = timezone.now()
        month_ago = now - timedelta(days=30)
        aggs = qs.aggregate(
            avg_rating=Avg('rate', default=0),
            highest_rate=Max('rate', defailt=0),
            lowest_rate=Min('rate', default=0),
            requests_per_month=Count("*")
        )
        daily = (
            qs
            .annotate(day=TruncDay('created'))
            .values('day')
            .annotate(
                avg_rating=Avg('rate'),
                count=Count('id')
            )
            .order_by('day')
        )
        rating_graph = [
            {'date': d['day'].strftime('%d.%m'),
             'value': round(d['avg_rating'] or 0, 2)}
            for d in daily
        ]
        requests_graph = [
            {'date': d['day'].strftime('%d.%m'), 'value': d['count']}
            for d in daily
        ]
        online_days = (
            qs.annotate(solved_date=TruncDate('created'))
            .values('solved_date')
            .distinct()
            .count()
        )
        extra_stats = self.get_extra_stats(obj, qs)
        stats = {
            "avg_rating": round(aggs['avg_rating'] or 0, 2),
            "highest_rate": aggs['highest_rate'] or 0,
            "lowest_rate": aggs['lowest_rate'] or 0,
            "requests_per_month": aggs['requests_per_month'],
            "online_days": {online_days},
            "rating_graph": rating_graph,
            "requests_graph": requests_graph,
            **extra_stats,
        }
        payload = {"info": info, "stats": stats}
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=200)

    def get_queryset_for_obj(self, obj):
        """
        This should be overridden in children if needed.
        Returns the QuerySet associated with the object
        """
        raise NotImplementedError("You must implement get_qs_for_obj()")

    def get_extra_info(self, obj, qs):

        return {}

    def get_extra_stats(self, obj, qs):

        return {}


class AgentInfoView(StatsView):
    model = AgentModel
    serializer_class = local_serializers.AgentStatsResponseSerializer

    def get_queryset_for_obj(self, obj):
        return RequestModel.objects.filter(solved_by=obj)

    def get_extra_info(self, obj, qs):
        return {"last_online": obj.last_online}

    def get_extra_stats(self, obj, qs):
        online_days = (
            qs.annotate(solved_date=TruncDate('created'))
            .values('solved_date')
            .distinct()
            .count()
        )
        return {"online_days": online_days}


class BotInfoView(StatsView):
    model = BotModel
    serializer_class = local_serializers.BotStatsResponseSerializer

    def get_queryset_for_obj(self, obj):
        return RequestModel.objects.filter(bot=obj)

    def get_extra_info(self, obj: BotModel, qs):
        added = (
            obj.created
        )
        security_key = obj.secret_key
        return {"added": added, "security_key": security_key}

    def get_extra_stats(self, obj, qs):
        agent = (
            RequestModel.objects
            .filter(is_solved=True)
            .annotate(solved_count=Count('solved_by'))
            .order_by('-solved_count')
            .first()
        )
        online_days = (
            qs.annotate(solved_date=TruncDate('created'))
            .values('solved_date')
            .distinct()
            .count()
        )
        extra_stats = {
            "online_days": online_days,
            "most_active_agent": f"{agent.solved_by.name}, {agent.solved_by.surname} ("
                                 f"{agent.solved_by.username})"
        }
        return extra_stats


class GroupInfoView(StatsView):
    model = GroupModel
    serializer_class = local_serializers.GroupStatsResponseSerializer

    def get_queryset_for_obj(self, obj):
        return RequestModel.objects.filter(bot__groups=obj)

    def get_extra_info(self, obj, qs):
        created = obj.created
        return {"created": created}

    def get_extra_stats(self, obj, qs):
        agent = (
            RequestModel.objects
            .filter(is_solved=True)
            .annotate(solved_count=Count('solved_by'))
            .order_by('-solved_count')
            .first()
        )
        online_days = (
            qs.annotate(solved_date=TruncDate('created'))
            .values('solved_date')
            .distinct()
            .count()
        )
        extra_stats = {
            "online_days": online_days,
            "most_active_agent": f"{agent.solved_by.name}, {agent.solved_by.surname} ("
                                 f"{agent.solved_by.username})"
        }
        return extra_stats


# / Get stats


# Get objects
class ObjectView(GenericAPIView):
    model = None
    name = None
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        group_id = request.data.get("id")
        if not group_id:
            return Response({"error": "Invalid or missing id"},
                            status=400)

        try:
            group = GroupModel.objects.get(id=group_id, agents__id=request.user.id)
        except GroupModel.DoesNotExist:
            return Response({"error": "Group not found"},
                            status=404)
        qs = getattr(group, self.name).all()
        if qs:
            serializer = self.serializer_class(qs, many=True)
            return Response(serializer.data, status=200)
        else:
            return Response({"error": "Model not found"}, status=404)


class BotListView(ObjectView):
    model = BotModel
    serializer_class = local_serializers.ObjectSerializer
    name = "bots"


class AgentListView(ObjectView):
    model = AgentModel
    serializer_class = local_serializers.ObjectSerializer
    name = "agents"

# / Get objects
