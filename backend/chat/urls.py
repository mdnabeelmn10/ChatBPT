from django.urls import path
from .views import chat_with_gpt,chat_history

urlpatterns = [
    path('chat/', chat_with_gpt, name='chat'),
    path('chat/history/', chat_history,name='history'),
]
