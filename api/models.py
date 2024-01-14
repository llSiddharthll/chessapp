# models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('I', 'In Progress'),
        ('C', 'Complete'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games')
    turn = models.CharField(max_length=1, choices=(('W', 'White'), ('B', 'Black')))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    last_move_time = models.DateTimeField(null=True)
    moves = models.TextField()  # Store move history in a text field

class Piece(models.Model):
    TYPE_CHOICES = (
        ('K', 'King'),
        ('Q', 'Queen'),
        ('R', 'Rook'),
        ('B', 'Bishop'),
        ('N', 'Knight'),
        ('P', 'Pawn'),
    )

    COLOR_CHOICES = (
        ('W', 'White'),
        ('B', 'Black'),
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    color = models.CharField(max_length=1, choices=COLOR_CHOICES)
    rank = models.IntegerField()
    file = models.CharField(max_length=1)  # Store file (column) as a character

    def __str__(self):
        return f"{self.color}{self.type} at {self.file}{self.rank}"


class ChessGame(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_player')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_player')
    board_state = models.TextField()
    current_turn = models.CharField(max_length=5, choices=[('white', 'White'), ('black', 'Black')], default='white')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    elo_rating = models.IntegerField(default=1000)

class Move(models.Model):
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    move = models.CharField(max_length=5) 
    timestamp = models.DateTimeField(auto_now_add=True)
    move_number = models.PositiveIntegerField()
