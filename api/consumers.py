import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the game_id from the URL
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"chess_game_{self.game_id}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connection established for game {self.game_id}")

        # Send a message to initialize the game
        await self.send(text_data=json.dumps({'action': 'init_game'}))

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket connection closed with code {close_code} for game {self.game_id}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'move_piece':
                # Handle the logic for moving chess pieces
                piece_id = data.get('pieceId')
                target_square_id = data.get('targetSquareId')

                # Update the game state or broadcast the move to other players
                # Your chess logic goes here

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chess.move_piece',
                        'piece_id': piece_id,
                        'target_square_id': target_square_id,
                    }
                )
            else:
                print("Invalid action format")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            await self.send(text_data=json.dumps({'error': 'Invalid JSON format'}))
        except Exception as e:
            print(f"Error during WebSocket receive: {e}")
            await self.send(text_data=json.dumps({'error': 'Internal server error'}))

    # Receive message from room group
    async def chess_move_piece(self, event):
        piece_id = event['piece_id']
        target_square_id = event['target_square_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'move_piece',
            'pieceId': piece_id,
            'targetSquareId': target_square_id,
        }))
