from django.urls import path
import api.v1.bot.views as views

urlpatterns = [
    path('create-request/', views.CreateRequestView.as_view(),
         name="create-request/")
]
