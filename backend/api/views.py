from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .utils import get_jwt_tokens

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = RegisterSerialier(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_jwt_tokens(user)
            return Response(tokens, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
