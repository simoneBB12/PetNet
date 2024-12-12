from django.contrib import admin
from django.conf import settings 
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('update_post/<int:post_id>/', views.update_post, name='update_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like_post/', views.like_post, name='like_post'),
    path('get_comments/<int:post_id>/', views.get_comments, name='get_comments'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('explore/', views.search_friends, name='search_friends'),
    path('contact/', views.contact, name='contact'),
    path('events/', views.events, name='events'),
    path('events/api/create', views.create_event, name='create_event'),
    path('events/api/list', views.list_events, name='list_events'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('addpet/', views.addpet, name='addpet'),
    path('editpet/', views.edit_pet, name='editpet'),
    path('delete_pet/<int:pet_id>/', views.delete_pet, name='delete_pet'),
    #for changing username
    path('settings/change_username/', views.change_username, name='change_username'),
    # friends system
    # catches the integer and assign it to request_id and pass it to send_friend_request
    path('accept_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/', views.friends_and_requests, name='friends'),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('messages/<int:friend_id>/', views.messages_view, name='messages_view'),
    path('logout/', LogoutView.as_view(), name='logout'),
]   + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


