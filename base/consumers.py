from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string, get_template
from asgiref.sync import async_to_sync
import json
from .models import *

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        
        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        
        self.accept()
        
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count() 
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        message = GroupMessage.objects.create(
            body = body,
            author = self.user, 
            group = self.chatroom 
        )
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )
        
    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        html = render_to_string("private_message/partials/chat_message_p.html", context=context)
        # print(html)
        self.send(text_data=html)
        
        
    def update_online_count(self):
        online_count = self.chatroom.users_online.count() -1
        
        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)
        
    def online_count_handler(self, event):
        online_count = event['online_count']
        
        chat_messages = ChatGroup.objects.get(group_name=self.chatroom_name).chat_messages.all()[:30]
        author_ids = set([message.author.id for message in chat_messages])
        users = User.objects.filter(id__in=author_ids)
        
        context = {
            'online_count' : online_count,
            'chat_group' : self.chatroom,
            'users': users
        }
        html = render_to_string("chat/partials/online_count.html", context)
        self.send(text_data=html) 


from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync

class PongConsumer(WebsocketConsumer):
    players = []  # Track players connected
    score = {'player1': 0, 'player2': 0}  # Track scores
    game_active = True  # Track whether the game is active or over
    user = None  # Store user info
    room_no = 0  # Store room number
    room = None  # Store room object

    def connect(self):
        # Initialize user and room
        self.user = self.scope['user']
        self.room_no = self.scope['url_route']['kwargs']['room_no']
        self.room = get_object_or_404(Room, id=self.room_no)

        # Add player to the game
        if len(self.players) < 2:
            self.players.append(self)
            self.accept()

            # Assign player number
            if len(self.players) == 1:
                self.player = 1
            else:
                self.player = 2

            # Start game when both players are connected
            if len(self.players) == 2:
                self.start_game()
        else:
            self.close()

    def disconnect(self, close_code):
        if self in self.players:
            self.players.remove(self)

    def receive(self, text_data):
        if not self.game_active:  # Ignore messages if the game is over
            return

        data = json.loads(text_data)

        # Check if ball reset event and update scores
        if 'reset' in data:
            if data['reset'] == 'player1':
                self.score['player1'] += 1
            elif data['reset'] == 'player2':
                self.score['player2'] += 1

            # Check if either player has reached the points limit
            if self.score['player1'] >= self.room.points or self.score['player2'] >= self.room.points:
                self.end_game()

            # Broadcast score update to all players
            score_update = {
                'type': 'score_update',
                'player1_score': self.score['player1'],
                'player2_score': self.score['player2']
            }
            for player in self.players:
                player.send(text_data=json.dumps(score_update))

        # Broadcast the received data to both players
        for player in self.players:
            player.send(text_data=json.dumps(data))

    def start_game(self):
        # Send initial state to both players
        initial_state = {
            'paddle1': {'y': 0},
            'paddle2': {'y': 0},
            'ball': {'x': 0, 'y': 0},
            'score': self.score
        }
        for player in self.players:
            player.send(text_data=json.dumps({'type': 'state_update', **initial_state}))

    def end_game(self):
        # Mark game as inactive
        self.game_active = False

        # Determine the winner
        winner = 'player1' if self.score['player1'] >= self.room.points else 'player2'

        self.room.is_expired = True
        self.room.save()

        # Broadcast game-over message to all players
        game_over_message = {
            'type': 'game_over',
            'winner': winner,
            'player1_score': self.score['player1'],
            'player2_score': self.score['player2']
        }
        for player in self.players:
            player.send(text_data=json.dumps(game_over_message))
