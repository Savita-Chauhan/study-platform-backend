from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'message': '🎓 AI Study Platform API',
        'status': 'Live',
        'developer': 'Savita Chauhan',
        'github': 'https://github.com/Savita-Chauhan/study-platform-backend',
        'endpoints': {
            'register': '/api/users/register/',
            'login': '/api/users/login/',
            'courses': '/api/courses/',
            'payments': '/api/payments/create-order/',
            'chatbot': '/api/chatbot/chat/',
            'certificates': '/api/certificates/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/quiz/', include('quiz.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/chatbot/', include('chatbot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)