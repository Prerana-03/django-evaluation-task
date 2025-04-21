import os
import sys
import django

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appdownloader.settings')

# Initialize Django
django.setup()

# Run database migrations if needed
from django.core.management import execute_from_command_line
try:
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
except Exception as e:
    print(f"Error during migration: {e}")

# Import and run Django's WSGI application
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()