import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# Auto migrate on startup
from django.core.management import call_command
call_command('migrate', '--run-syncdb')

# Create superuser only if not exists
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin10',
        email='chauhansavita711@gmail.com',
        password='Admin10@1234'
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists - skipping!")