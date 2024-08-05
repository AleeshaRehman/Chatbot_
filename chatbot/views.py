from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Chat, Message, Prompt, Response
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

# from .rag_chatbot import GPT2Chatbot
from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes

#gpt_chatbot = GPT2Chatbot()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny  # Import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home(request):
    return Response({"message": "Welcome to the Chatbot application!"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_chat(request):
    data = json.loads(request.body)
    user = request.user
    chat = Chat.objects.create(user=user, title=data.get('title', ''))
    return JsonResponse({'chat_id': chat.chat_id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    data = json.loads(request.body)
    chat = get_object_or_404(Chat, pk=data['chat_id'])
    message = Message.objects.create(
        chat=chat,
        sender=data['sender'],
        text=data['text']
    )
    
    if data['sender'] == 'user':
        response_text = gpt_chatbot.generate_response(data['text'])
        Response.objects.create(chat=chat, text=response_text)
    
    return JsonResponse({'message_id': message.id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    history = [{'sender': msg.sender, 'text': msg.text, 'timestamp': msg.timestamp} for msg in messages]
    return JsonResponse({'history': history})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_chats(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    chats = Chat.objects.filter(user=user).order_by('-created_at')
    chat_list = [{'chat_id': chat.chat_id, 'title': chat.title, 'created_at': chat.created_at} for chat in chats]
    return JsonResponse({'chats': chat_list})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)
    chat.delete()
    return JsonResponse({'status': 'success', 'message': 'Chat deleted'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    message.delete()
    return JsonResponse({'status': 'success', 'message': 'Message deleted'})
