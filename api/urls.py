from django.urls import path
from . import views

app_name = 'api'  # This helps to namespace your app's URLs

urlpatterns = [
    path('', views.index, name="home"),
    path('api/login/', views.api_login, name='api_login'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/logout/', views.user_logout, name='user_logout'),
    path('api/play_with_user/<str:opponent_username>/', views.play_with_user, name='play_with_user'),
    path('api/play_with_bot/', views.play_with_bot, name='play_with_bot'),
    path('api/handle_user_move/', views.handle_user_move, name='handle_user_move'),
    path('api/handle_bot_move/', views.handle_bot_move, name='handle_bot_move'),
    path('api/chess_games/', views.ChessGameView.as_view(), name='chess_games'),
    path('api/users/', views.UserView.as_view(), name='users'),
]
