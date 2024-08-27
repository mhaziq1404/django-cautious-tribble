from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
from .models import Room

logger = logging.getLogger(__name__)

# @receiver(post_save, sender=Room)
# def create_room(sender, instance, created, **kwargs):
#     if created:
#         event = {
#             "type": "notification_handler",
#             "room_id": instance.id,
#             "room_name": instance.name,
#             "description": instance.description,
#             "host": instance.host.username if instance.host else None,
#         }
        
#         channel_layer = get_channel_layer()
#         group_name = f'user-notifications-{instance.host.id}' if instance.host else 'user-notifications'
        
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 "type": "notification_handler",
#                 "event": event
#             }
#         )