from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import FriendRequest, FriendList, Message
from .forms import PostForm, CommentForm
from .models import Post, Comment
from .models import Pet
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Event
from django.views import View
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import Http404

def home(request):
    posts = Post.objects.all().order_by('-created_at')

    post_form = PostForm()
    comment_form = CommentForm()

    if request.method == "POST":
        # Handle new post creation
        if 'post_form' in request.POST:
            post_form = PostForm(request.POST, request.FILES)  
            
            if post_form.is_valid():
                post = post_form.save(commit=False)  
                post.author = request.user  
                post.save()  
                return redirect('home')  
            else:
                print("Form errors:", post_form.errors)  

        elif 'comment_form' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                post_id = request.POST.get('post_id')
                post = get_object_or_404(Post, id=post_id)
                comment = comment_form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()

                comment_data = {
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }

                return JsonResponse({'status': 'success', 'comment': comment_data})

    return render(request, 'blog/home.html', {
        'posts': posts,  
        'post_form': post_form,  
        'comment_form': comment_form,  
    })

@login_required
def update_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, author=request.user)
        data = json.loads(request.body)
        new_content = data.get('content', '').strip()

        if not new_content:
            return JsonResponse({'status': 'error', 'message': 'Post content cannot be empty.'})

        post.content = new_content
        post.save()
        return JsonResponse({'status': 'success', 'new_content': new_content})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, author=request.user)
        post.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def like_post(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        # Toggle like/unlike
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({'status': 'success', 'liked': liked, 'like_count': post.like_count()})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@login_required
def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('created_at')

    comment_list = [
        {
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for comment in comments
    ]
    return JsonResponse({'status': 'success', 'comments': comment_list})

def about(request):
    return render(request, 'blog/about.html')

@login_required(login_url='login')
def settings(request):
    pets = Pet.objects.filter(user=request.user)  
    return render(request, 'blog/settings.html', {'pets': pets})

def contact(request):
    return render(request, 'blog/contact.html')

def events(request):
    return render(request, 'blog/events.html')

def edit_pet(request):
    pets = Pet.objects.filter(user=request.user)   
    return render(request, 'blog/editpet.html', {'pets': pets})
#Pets
@login_required
def addpet(request):
    if request.method == 'POST':
        pet_name = request.POST.get('pet_name')
        pet_species = request.POST.get('pet_species')
        pet_image = request.FILES.get('pet_image')

        # Create the pet instance and associate it with the logged-in user
        pet_instance = Pet.objects.create(
            name=pet_name,
            species=pet_species,
            image=pet_image,
            user=request.user  # Ensure the pet is associated with the logged-in user
        )

        # Redirect to the profile page after adding the pet
        return redirect('profile')  # Redirect to the 'profile' view after adding the pet

    return render(request, 'blog/addpet.html')  # Render the add pet form

@login_required
def profile(request):
    user = request.user
    Pets = Pet.objects.filter(user=user)
    user_posts = Post.objects.filter(author=user).order_by('-created_at')
    post_count = user_posts.count()

    # Ensure FriendList exists for the user
    friend_list, created = FriendList.objects.get_or_create(user=user)
    friends = friend_list.friends.all()
    followers_count = friends.count()

    return render(request, 'blog/profile.html', {
        'user': user,
        'Pets': Pets,
        'user_posts': user_posts,
        'post_count': post_count,
        'followers_count': followers_count,
        'friends': friends,
    })

@login_required
def change_username(request):
    if request.method == 'POST':
        new_username = request.POST['new_username']
        user = request.user
        try:
            user.username = new_username
            user.save()
            messages.success(request, 'Username changed successfully!')
        except Exception as e:
            messages.error(request, 'An error occurred while changing the username.')
        return redirect('settings')  
    return render(request, 'blog/settings.html')  

def search_friends(request):
    # Get the 'query' from the GET request and if nothing is received an empty string will be the default value
    query = request.GET.get('query', '')  
    # store the search result
    results = []
    # will happen if query is not an empty string
    if query:
        # Perform the search based on the username (case insensivite) using the query 
        # equivalent to sql code = SELECT * FROM auth_user WHERE username ILIKE 'query'
        results = User.objects.filter(username__icontains=query)
    
    # If the request is POST and 'add_friend' is in POST data, handle friend request creation
    if request.method == 'POST' and 'add_friend' in request.POST:
        # Retrieve the 'receiver_id' from the form data to send a friend request
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(User, id=receiver_id)
        # Check to avoid sending a friend request to self
        if receiver != request.user:
            # Create a FriendRequest from the current user to the receiver
            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            return redirect('search_friends')
    
    # return the request, query and results
    return render(request, 'blog/explore.html', {'query': query, 'results': results})


@login_required
def accept_friend_request(request, request_id):
    # retrieve an instance of the FriendRequest model with a specific id from friends.html
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    # Ensure only the receiver can accept the friend request
    if friend_request.receiver == request.user:
        friend_request.accept()
    return redirect('friends')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.receiver == request.user:
        friend_request.decline()
    return redirect('friends')

@login_required
def friends_and_requests(request):
    # Retrieve the friend list for the logged-in user, or create an empty list if it doesn’t exist
    try:
        friend_list = FriendList.objects.get(user=request.user).friends.all()
    except FriendList.DoesNotExist:
        friend_list = []

    # Retrieve all pending friend requests sent to the logged-in user
    friend_requests = FriendRequest.objects.filter(receiver=request.user, is_active=True)

    return render(request, 'blog/friends.html', {
        'friends': friend_list,
        'friend_requests': friend_requests
    })

@login_required
def delete_pet(request, pet_id):
    if request.method == 'POST':
        pet_instance = get_object_or_404(Pet, id=pet_id, user=request.user)
        pet_instance.delete()  # Delete the pet instance
        return redirect('editpet')  # Redirect back to the editpet page

    
    else:
        raise Http404("Pet not found.")

def recommendation(request):
    return render(request, 'blog/recommendation.html')

@login_required
def messages_view(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    try:
        friend_list = FriendList.objects.get(user=request.user).friends.all()
    except FriendList.DoesNotExist:
        friend_list = []
    messages = Message.objects.filter( # Filters messages between the logged-in user and the specified friend
        (models.Q(sender=request.user, receiver=friend) | models.Q(sender=friend, receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=friend, content=content)
            return redirect('messages_view', friend_id=friend.id)

    return render(request, 'blog/messages.html', {'friend': friend, 'messages': messages, 'friends' : friend_list})

@csrf_exempt 
def create_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            date = data.get('date')

            if not title or not date:
                return JsonResponse({'error': 'Title and date are required'}, status=400)

            event = Event.objects.create(title=title, date=date)
            return JsonResponse({'id': event.id, 'title': event.title, 'date': event.date})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def list_events(request):
    user_events = Event.objects.filter(user=request.user)
    events_data = []

    for event in user_events:
        events_data.append({
            'title': event.title,
            'start': event.date.isoformat(),
        })

    return JsonResponse({'events': events_data})

# View for displaying events and handling the deletion
def event_list(request):
    events = Event.objects.all()  # Fetch all events
    return render(request, 'blog/events.html', {'events': events})

# View for deleting an event
def delete_event(request, event_id):
    if request.method == 'POST':
        try:
            event = Event.objects.get(id=event_id)  # Get the event by ID
            event.delete()  # Delete the event
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        
