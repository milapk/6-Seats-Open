from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .serializers import *
from .utils import get_jwt_tokens, game_matchmaking
from .models import *

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = RegisterSerialier(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            player = PlayerModel.objects.create(user=user)
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
    
class ClaimChipsView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        if user.claim_chips():
            user = CustomUser.objects.get(id=user.id)
            return Response({'chips': user.chips}, status=status.HTTP_200_OK)
        else:
            cool_down = user.get_claim_cooldown()
            return Response({'cool_down': cool_down}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
class JoinGameView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        small_blind = request.data.get('small_blind')
        if not small_blind:
            return Response({'error': 'Request must contain "small_blind"'}, status=status.HTTP_400_BAD_REQUEST)
        big_blind = request.data.get('big_blind')
        if not big_blind:
            return Response({'error': 'Request must contain "big_blind"'}, status=status.HTTP_400_BAD_REQUEST)
        buy_in = request.data.get('buy_in')
        if not buy_in:
            return Response({'error': 'Request must contain "buy_in"'}, status=status.HTTP_400_BAD_REQUEST)
        elif buy_in > user.chips:
            return Response({'error': f'Requested buy in was {buy_in} while User only has {user.chips} chips'}, status=status.HTTP_400_BAD_REQUEST)
        
        table_type = TableTypeModel.objects.filter(small_blind=small_blind, big_blind=big_blind)
        if not table_type.exists():
            return Response({'error': 'Games with stakes given do not exist'}, status=status.HTTP_400_BAD_REQUEST)
        elif table_type.min_buy_in > buy_in:
            return Response({'error': f'Buy in must be greater than {table_type.min_buy_in}'}, status=status.HTTP_400_BAD_REQUEST)
        elif table_type.max_buy_in < buy_in:
            return Response({'error': f'Buy in must be less than {table_type.max_buy_in}'}, status=status.HTTP_400_BAD_REQUEST)
        
        player = PlayerModel.objects.get(user=user)
        if player.game is not None:
            return Response({'error': 'User already in a game, please leave game before joining another one'}, status=status.HTTP_400_BAD_REQUEST)
        
        game = game_matchmaking()
        if not game:
            game = GameModel.objects.create(table_type=table_type, num_of_players=1)
        player.game = game
        user.chips -= buy_in
        player.chip_in_play = buy_in
        user.save(update_fields=['chips'])
        #asssign player a seat
        return Response({'success': f'Join Game:{game.id} successfully'}, status=status.HTTP_200_OK)