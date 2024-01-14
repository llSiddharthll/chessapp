from rest_framework import serializers
from .models import ChessGame, User

class ChessGameSerializer(serializers.ModelSerializer):
   class Meta:
       model = ChessGame
       fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
   class Meta:
       model = User
       fields = '__all__'
