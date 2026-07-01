# backend/chatbot/urls.py

from django.urls import path
from .views import ChatbotView, GenerateQuizView

urlpatterns = [
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('generate-quiz/', GenerateQuizView.as_view(), name='generate-quiz'),
]