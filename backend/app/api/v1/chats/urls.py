from django.urls import path
import api.v1.chats.views as views

urlpatterns = [
    path('get-chat-list/', views.ChatListView.as_view(),
         name="get-chat-list/"),
    path('get-group-list/', views.GroupListView.as_view(),
         name="get-group-list/"),
    path('get-chat-messages/', views.ChatMessageList.as_view(),
         name="get-chat-messages/")
]
