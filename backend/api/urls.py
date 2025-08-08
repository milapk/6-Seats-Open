from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import *

urlpatterns = [
    path('obtain-token/', TokenObtainPairView.as_view(), name='obtain_token'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh_token'),
    path('register/', RegisterView.as_view(), name='register'),
]