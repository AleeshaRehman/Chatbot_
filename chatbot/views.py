from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from .models import Chat, Message, Response
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import json

class HomePageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return DRFResponse({"message": "Welcome to Chatbot Application!"}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return DRFResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return DRFResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return DRFResponse({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return DRFResponse({"detail": "Method not allowed. Please use POST."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message, Response
import json

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    logger.info("Received request: %s", request)
    logger.info("Request Headers: %s", request.headers)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON: %s", request.body)
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    chat_id = data.get('chat_id')
    text = data.get('text')
    sender = data.get('sender')

    if not chat_id or not text or not sender:
        return JsonResponse({'error': 'Required fields are missing'}, status=400)

    chat = get_object_or_404(Chat, pk=chat_id)

    # Check if the same message already exists in the chat
    if Message.objects.filter(chat=chat, text=text, sender=sender).exists():
        return JsonResponse({'error': 'Message already exists'}, status=400)

    # Create the user message
    message = Message.objects.create(
        chat=chat,
        sender=sender,
        text=text,
        user=request.user
    )

    response_text = None
    if sender == 'user':
        try:
            # Call Mistral API for response
            api_key = ""
            model = "mistral-large-latest"
            client = MistralClient(api_key=api_key)
            chat_response = client.chat(
                model=model,
                messages=[ChatMessage(role="user", content=text)]
            )
            response_text = chat_response.choices[0].message.content
            # Store the chatbot response
            Response.objects.create(chat=chat, text=response_text)
        except Exception as e:
            logger.error("Error with Mistral API: %s", e)
            return JsonResponse({'error': 'Error with Mistral API'}, status=500)

    return JsonResponse({
        'message': 'Message sent',
        'message_id': message.id,
        'response_text': response_text
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_chat(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    chat = Chat.objects.create(user=request.user, title=data.get('title', ''))
    return JsonResponse({'chat_id': chat.chat_id})

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


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return JsonResponse({'error': 'No refresh token provided'}, status=400)

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()  # This method requires django-rest-framework-simplejwt to be configured with blacklisting.

        return JsonResponse({'message': 'Successfully logged out'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


