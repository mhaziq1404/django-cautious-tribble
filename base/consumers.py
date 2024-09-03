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
    def connect(self):
        self.room_group_name = 'pong_room'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        # Initial game state
        self.game_state = {
            'paddle1': {'y': 0},
            'paddle2': {'y': 0},
            'ball': {'x': 0, 'y': 0},
            'ball_speed': 0.1,
            'ball_angle': 180,
            'score1': 0,
            'score2': 0,
        }

        # Send current game state to the newly connected client
        self.send(text_data=json.dumps({
            'type': 'state_update',
            'game_state': self.game_state
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'move_paddle':
            player_id = data['player_id']
            position = data['position']

            # Update the paddle's position
            if player_id == 1:
                self.game_state['paddle1']['y'] = position
            elif player_id == 2:
                self.game_state['paddle2']['y'] = position

            # Broadcast the new game state
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_state_update',
                    'game_state': self.game_state
                }
            )

        elif message_type == 'update_ball':
            # Additional checks or updates can be handled here
            self.game_state['ball'] = data['ball']
            self.check_ball_reset()

    def check_ball_reset(self):
        # Check if ball crosses the reset line and reset if necessary
        if abs(self.game_state['ball']['x']) > 2.45:  # Example reset condition
            self.game_state['ball']['x'] = 0
            self.game_state['ball']['y'] = 0

    def send_state_update(self, event):
        game_state = event['game_state']

        # Send updated state to all clients
        self.send(text_data=json.dumps({
            'type': 'state_update',
            'game_state': game_state
        }))
