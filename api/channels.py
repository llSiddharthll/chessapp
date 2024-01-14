import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game

class ChessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join a game room based on a URL parameter
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        # Add the consumer to the game room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the consumer from the game room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'make_move':
            game_id = text_data_json['game_id']
            move = text_data_json['move']

            # Validate and process the move (using game logic functions)
            is_valid, error_message = await self.validate_and_process_move(game_id, move)

            if is_valid:
                # Broadcast the move to both players in the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'move_made',
                        'move': move,
                    }
                )
            else:
                # Send an error message back to the player who made the move
                await self.send(text_data=json.dumps({'error': error_message}))

    # Helper function to validate and process a move
    async def validate_and_process_move(self, game_id, move):
        # Retrieve the game object
        game = await Game.objects.get(id=game_id)

        # Implement your game logic to validate the move and update the game state
        # ...

        return True, ""  # Replace with appropriate return values based on move validation

    # Handler for receiving broadcasted move updates
    async def move_made(self, event):
        move = event['move']
        await self.send(text_data=json.dumps({'type': 'move_made', 'move': move}))
