import os
import django
from django.contrib.auth import get_user_model
from django.db import IntegrityError

# Initialise django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()


User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

if username and email and password:
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser {username} created successfully.")
    except IntegrityError:
        print(f"Superuser {username} already exists.")
else:
    print("Superuser credentials not set.")
