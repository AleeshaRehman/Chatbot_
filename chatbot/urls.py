from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('chat-history/<int:chat_id>/', views.chat_history, name='chat_history'),
    path('user-chats/<int:user_id>/', views.user_chats, name='user_chats'),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
]
