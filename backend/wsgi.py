import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# Auto migrate + create superuser on startup
from django.core.management import call_command
call_command('migrate', '--run-syncdb')

# Create superuser automatically
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin2',
        email='chauhansavita711@gmail.com',
        password='Admin2@1234'
    )