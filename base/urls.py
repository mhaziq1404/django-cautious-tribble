from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Authentication
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    # Home and User Profile
    path('', views.home, name="home"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('update-user/', views.updateUser, name="update-user"),
    path('ai_playnow/', views.ai_playnow, name="ai_playnow"),
    path('join_room/', views.join_room, name="join_room"),

    # Room Management
    path('room/<str:pk>/', views.room, name="room"),
    path('room_list/', views.room_list, name="room_list"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('player-list/<int:room_id>/', views.player_list, name='player_list'),
    path('leave-room/', views.leave_room, name='leave_room'),
    path('kick-player/', views.kick_player, name='kick_player'),
    path('check-kickout-status/', views.check_kickout_status, name='check_kickout_status'),

    # Chat Functionality
    path('pong/<str:pk>/', views.pongPage, name="pong"),
    path('chat/new_groupchat/', views.create_groupchat, name="new-groupchat"),
    path('chat/<username>/', views.get_or_create_chatroom, name="start-chat"),
    path('chat/edit/<chatroom_name>/', views.chatroom_edit_view, name="edit-chatroom"),
    path('chat/delete/<chatroom_name>/', views.chatroom_delete_view, name="chatroom-delete"),
    path('chat/leave/<chatroom_name>/', views.chatroom_leave_view, name="chatroom-leave"),
    path('chat/fileupload/<chatroom_name>/', views.chat_file_upload, name="chat-file-upload"),
    path('messages/', views.chat_ui, name="messages"),
    path('messages/<int:id>/', views.chat_group_detail, name='chat_group_detail'),
    path('messages/create_privchat/<str:user_id>/', views.create_privatechat, name='create_privatechat'),
    path('invite/', views.invite_through_message, name='invite_through_message'),
    path('block/<str:pk>/', views.block_group, name='block_group'),

    # tournament
    path('room/tournament/<str:pk>/', views.tournament_view, name='tournament_view'),
    path('room/<int:pk>/podium/', views.podium_view, name='podium_view'),

    # friends
    path('add_friend/<str:user_id>/', views.add_friend, name='add_friend'),
    path('remove_friend/<str:user_id>/', views.remove_friend, name='remove_friend'),
    path('cancel-friend-request/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),

    # notifications
    path('notifications/read/<int:notification_id>/', views.friend_mark_as_read, name='friend_mark_as_read'),
    path('noti_list/', views.noti_list, name="noti_list"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('test/', views.pong_game_view, name='pong_game'),
]

