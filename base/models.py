from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import shortuuid
from PIL import Image
import os
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, default="The User too lazy to add a Bio")
    avatar = models.ImageField(null=True, default="avatar.svg")
    group_chats = models.ManyToManyField('ChatGroup', related_name='group_members', blank=True)
    blocked_groups = models.ManyToManyField('ChatGroup', related_name='blocked_users', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def add_friend(self, friend):
        if not Friend.objects.filter(user=self, friend=friend).exists():
            Friend.objects.create(user=self, friend=friend)

    def remove_friend(self, friend):
        try:
            friendship = Friend.objects.get(user=self, friend=friend)
            friendship.delete()
        except Friend.DoesNotExist:
            pass

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friend_set', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='related_friend_set', on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f"{self.user} - {self.friend}"

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=1)
    invitation_link = models.CharField(max_length=255, unique=True, blank=True, null=True)

    OPPONENT_TYPE_CHOICES = (
        ('vs Player', 'vs Player'),
        ('Tournament', 'Tournament'),
        ('AI', 'AI'),
    )
    opponent_type = models.CharField(max_length=10, choices=OPPONENT_TYPE_CHOICES, default='AI')
    won_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_by_user')
    won_by_ai = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    host_ready = models.BooleanField(default=False)
    opp_ready = models.BooleanField(default=False)
    is_2player = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invitation_link:
            self.invitation_link = str(uuid.uuid4())
        super().save(*args, **kwargs)

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, default=None)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name

    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = shortuuid.uuid()
        super().save(*args, **kwargs)

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    is_invitation = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, default=None)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None

    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'

    class Meta:
        ordering = ['-created']

    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except (IOError, SyntaxError):
            return False

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_player2')
    player1_score = models.IntegerField(null=True, blank=True)
    player2_score = models.IntegerField(null=True, blank=True)
    round = models.CharField(max_length=20)
    is_final = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    winner = models.ForeignKey(User, related_name='match_winner', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.player1} vs {self.player2} - {self.round}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('friend_request', 'Friend Request'),
        ('friend_request_accepted', 'Friend Request Accepted'),
        # Add more types as needed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"
