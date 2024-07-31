from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Chat, Message, Prompt, Response
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

@csrf_exempt
def new_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = get_object_or_404(User, pk=data['user_id'])
        chat = Chat.objects.create(user=user, title=data.get('title', ''))
        return JsonResponse({'chat_id': chat.chat_id})

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat = get_object_or_404(Chat, pk=data['chat_id'])
        message = Message.objects.create(
            chat=chat,
            sender=data['sender'],
            text=data['text']
        )
        return JsonResponse({'message_id': message.id})

def chat_history(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    history = [{'sender': msg.sender, 'text': msg.text, 'timestamp': msg.timestamp} for msg in messages]
    return JsonResponse({'history': history})

def user_chats(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    chats = Chat.objects.filter(user=user).order_by('-created_at')
    chat_list = [{'chat_id': chat.chat_id, 'title': chat.title, 'created_at': chat.created_at} for chat in chats]
    return JsonResponse({'chats': chat_list})

from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Chatbot application!")

@csrf_exempt
def delete_chat(request, chat_id):
    if request.method == 'DELETE':
        chat = get_object_or_404(Chat, pk=chat_id)
        chat.delete()
        return JsonResponse({'status': 'success', 'message': 'Chat deleted'})

@csrf_exempt
def delete_message(request, message_id):
    if request.method == 'DELETE':
        message = get_object_or_404(Message, pk=message_id)
        message.delete()
        return JsonResponse({'status': 'success', 'message': 'Message deleted'})
