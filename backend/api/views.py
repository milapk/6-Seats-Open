from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .serializers import *
from .utils import get_jwt_tokens
from .models import *

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = RegisterSerialier(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh, access = get_jwt_tokens(user)
            return Response({'refresh': refresh, 'access': access, 'chips': user.chips}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetTableDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user = request.user
        data = (TableTypeModel.objects.annotate(
            game_count=Count('gamemodel', distinct=True),
            total_players=Count('gamemodel__playermodel', distinct=True)
            ).values('big_blind', 'small_blind', 'min_buy_in','game_count', 'total_players'))
        data = [{'big_blind': item['big_blind'], 'small_blind': item['small_blind'],'buy_in': item['min_buy_in'],'games': item['game_count'], 'players': item['total_players']} for item in data]
        return Response({'table_data': data, 'chips': user.chips}, status=status.HTTP_200_OK)