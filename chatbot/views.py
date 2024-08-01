from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Chat, Message, Prompt, Response
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

from .rag_chatbot import GPT2Chatbot
from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout



from django.http import HttpResponse



# Initialize the GPT chatbot
gpt_chatbot = GPT2Chatbot()
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
        
        # Generate a response if the sender is the user
        if data['sender'] == 'user':
            response_text = gpt_chatbot.generate_response(data['text'])
            Response.objects.create(chat=chat, text=response_text)
        
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
    


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
    context = {"form": form}
    return render(request, "chatbot/signup.html", context)


def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            err = "Invalid Credentials"
    
    context = {"error": err}
    return render(request, "chatbot/signin.html", context)

def signout(request):
    logout(request)
    return redirect("signin")
