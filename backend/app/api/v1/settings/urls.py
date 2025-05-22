from django.urls import include, path
import api.v1.settings.views as views

urlpatterns = [
    path('get-bot-info/', views.BotInfoView.as_view(), name='get-bot-info'),
    path('get-agent-info/', views.AgentInfoView.as_view(),
         name='get-agent-info'),
    path('get-group-info/', views.GroupInfoView.as_view()),
    path('get-bot-list/', views.BotListView.as_view(), name='get-bot-list'),
    path('get-agent-list/', views.AgentListView.as_view(),
         name='get-agent-list'),
]
