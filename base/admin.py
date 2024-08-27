from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(User)
admin.site.register(Room)
admin.site.register(ChatGroup)
admin.site.register(GroupMessage)
admin.site.register(Friend)
admin.site.register(Notification)