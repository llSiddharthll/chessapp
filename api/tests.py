from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import ChessGame
from .serializers import ChessGameSerializer

class ChessGameViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create two users for testing
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')


    # Previous test cases

    def test_api_signup(self):
        url = reverse('api:api_signup')
        data = {'username': 'new_user', 'password': 'new_password'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)  # Check if a token is present in the response

    def test_api_login(self):
        # Assuming you have created a user with username 'user1'
        url = reverse('api:api_login')
        data = {'username': 'user1', 'password': 'password1'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)  # Check if a token is present in the response

    def test_play_with_user(self):
        url = reverse('api:play_with_user', args=['opponent_username'])
        self.client.force_login(self.user1)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions based on the expected response data

    def test_play_with_bot(self):
        url = reverse('api:play_with_bot')
        self.client.force_login(self.user1)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add more assertions based on the expected response data

    # You can add more tests for other views as needed
