from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
import chess
import chess.engine
from django.contrib.auth.forms import UserCreationForm
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

def index(request):
    return render(request,'index.html')

def generate_response(status, message):
    return JsonResponse({'status': status, 'message': message})

def handle_game_move(game, player, move):
    board = chess.Board(game.board_state)
    if chess.Move.from_uci(move) in board.legal_moves:
        board.push(chess.Move.from_uci(move))
    else:
        return generate_response('error', 'Invalid move.')

    game.board_state = board.fen()
    game.current_turn = game.player2 if player == game.player1 else game.player1
    game.save()

    return generate_response('success', f'{player.username}\'s move handled successfully.')

class ChessGameView(APIView):
   serializer_class = ChessGameSerializer

   @csrf_exempt
   def get(self, request, format=None):
       games = ChessGame.objects.all()
       serializer = ChessGameSerializer(games, many=True)
       return Response(serializer.data)

   @csrf_exempt
   def post(self, request, format=None):
       serializer = ChessGameSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
   @csrf_exempt
   def post(self, request, format=None):
       serializer = UserSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any user, even if they are not authenticated
def api_signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    form_data = {'username': username, 'password1': password, 'password2': password}
    form = UserCreationForm(form_data)
    
    if form.is_valid():
        user = form.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid form submission', 'details': form.errors}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@login_required
def user_logout(request):
   logout(request)
   return JsonResponse({'status': 'success', 'message': 'You have been logged out. See you next time!'})

@csrf_exempt
@login_required
def play_with_user(request, opponent_username):
   user = request.user
   opponent = User.objects.get(username=opponent_username)
   if user == opponent:
       return JsonResponse({'status': 'error', 'message': 'You cannot play with yourself.'})

   # Create a new chess game between the two users
   new_game = ChessGame(white_player=user, black_player=opponent)
   new_game.save()

   # Return the chess game data to the client
   serializer = ChessGameSerializer(new_game)
   return JsonResponse(serializer.data)

# Assuming you have the ChessGame and handle_game_move functions defined

@csrf_exempt
@login_required
@api_view(['POST'])
def play_with_bot(request):
    if request.method == 'POST':
        # Create a new chess game between the user and the bot
        game = ChessGame.objects.create(player1=request.user, is_bot_game=True)
        
        # Optionally, you can initialize the chess board with a starting position
        initial_board = chess.Board()
        game.board_state = initial_board.fen()
        game.current_turn = request.user
        game.save()

        # Bot makes the first move
        bot_move = get_stockfish_move(game.board_state)

        # Update the board state with the bot's move
        board = chess.Board(game.board_state)
        board.push(chess.Move.from_uci(bot_move))
        game.board_state = board.fen()
        game.current_turn = request.user  # Update the current turn to the user
        game.save()

        # Respond with the game ID and the initial bot move
        return JsonResponse({
            'status': 'success',
            'message': 'Chess game with bot started.',
            'game_id': game.id,
            'bot_move': bot_move,
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@api_view(['POST'])
def handle_user_move(request):
    if request.method == 'POST':
        game_id = request.data.get('game_id')
        move = request.data.get('move')

        try:
            game = ChessGame.objects.get(id=game_id)
        except ChessGame.DoesNotExist:
            return generate_response('error', 'Invalid game ID.')

        if game.current_turn != request.user:
            return generate_response('error', 'It is not your turn.')

        return handle_game_move(game, request.user, move)
    else:
        return generate_response('error', 'Invalid request method.')

def get_stockfish_move(board_state):
    # Create a chess.Board object from the FEN string
    board = chess.Board(board_state)

    # Set up the Stockfish engine
    with chess.engine.SimpleEngine.popen_uci("stockfish/") as engine:
        # Calculate the best move with a time limit of 2 seconds
        result = engine.play(board, chess.engine.Limit(time=2.0))

        # Return the best move in UCI (Universal Chess Interface) format
        return result.move.uci()

@api_view(['POST'])
def handle_bot_move(request):
    if request.method == 'POST':
        game_id = request.data.get('game_id')

        try:
            game = ChessGame.objects.get(id=game_id)
        except ChessGame.DoesNotExist:
            return generate_response('error', 'Invalid game ID.')

        if game.current_turn == game.player2 and game.is_bot_game:
            best_move = get_stockfish_move(game.board_state)

            board = chess.Board(game.board_state)
            board.push(chess.Move.from_uci(best_move))

            game.board_state = board.fen()
            game.current_turn = game.player1
            game.save()

            return generate_response('success', 'Bot move handled successfully.')
        else:
            return generate_response('error', 'It is not the bot\'s turn.')
    else:
        return generate_response('error', 'Invalid request method.')
