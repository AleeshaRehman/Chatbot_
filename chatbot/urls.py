from django.urls import path
from .views import RegisterView, new_chat, send_message, chat_history, user_chats, delete_chat, delete_message, LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import HomePageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', HomePageView.as_view(), name='home'),
    path('new-chat/', new_chat, name='new_chat'),
    path('send-message/', send_message, name='send_message'),
    path('chat-history/<int:chat_id>/', chat_history, name='chat_history'),
    path('user-chats/<int:user_id>/', user_chats, name='user_chats'),
    path('delete-chat/<int:chat_id>/', delete_chat, name='delete_chat'),
    path('delete-message/<int:message_id>/', delete_message, name='delete_message'),
]

