from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import localtime

class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    # Boolean field to track if the request is active (not yet accepted or declined)
    is_active = models.BooleanField(default=True)
    # Timestamp to record when the friend request is sent
    timestamp = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.is_active = False
        self.save()

        # Ensure FriendLists exist and add each user to the other's friend list
        sender_friend_list, created = FriendList.objects.get_or_create(user=self.sender)
        receiver_friend_list, created = FriendList.objects.get_or_create(user=self.receiver)

        sender_friend_list.add_friend(self.receiver)
        receiver_friend_list.add_friend(self.sender)

    def decline(self):
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self.sender} sent a friend request to {self.receiver}"

class FriendList(models.Model):
    # each user has only one friend list
    user = models.OneToOneField(User, related_name='friends', on_delete=models.CASCADE) 
    # each FirendList can contain multiple user instances and friends
    friends = models.ManyToManyField(User, blank=True)

    def add_friend(self, friend):
        self.friends.add(friend)

    def remove_friend(self, friend):
        self.friends.remove(friend)

    def __str__(self):
        return f"{self.user}'s friend list"
    
class Pet(models.Model):
    user = models.ForeignKey(User, related_name='pets', on_delete=models.CASCADE)  
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.species}) - Owned by {self.user.username}"
    
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

class Post(models.Model):
    author = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    image = models.FileField(upload_to='post_images/', blank = True, null = True)
    def __str__(self):
        return f'Post by {self.author} on {self.created_at}'
    
    def like_count(self):
        return self.likes.count()
    
    def created_at_local(self):
        return self.created_at.strftime('%B %d, %Y, %I:%M %p') 

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post}'


class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} on {self.date}"

