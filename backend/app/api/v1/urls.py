from django.urls import include, path
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # path('ws/', include('api.v1.chat.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/jwt/create/', jwt_views.TokenObtainPairView.as_view()),
    path('auth/jwt/refresh/', jwt_views.TokenRefreshView.as_view()),
    path('auth/jwt/verify/', jwt_views.TokenVerifyView.as_view()),
    path('settings/', include('api.v1.settings.urls')),
    path('chats/', include('api.v1.chats.urls')),
    path('bot/', include('api.v1.bot.urls'))
]
