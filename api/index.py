import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brainforge.settings")

from django.core.wsgi import get_wsgi_application

# Run migrations automatically on Vercel (database lives in /tmp)
if os.getenv("VERCEL"):
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command("migrate", "--run-syncdb", verbosity=0)
    except Exception:
        pass  # Migrations already applied or DB not needed yet

app = get_wsgi_application()

