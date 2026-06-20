import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brainforge.settings")

# On Vercel: run migrations and collectstatic BEFORE the WSGI app starts
# so WhiteNoise can find the static files when middleware initialises.
if os.getenv("VERCEL"):
    import django
    django.setup()
    from django.core.management import call_command
    try:
        call_command("migrate", "--run-syncdb", verbosity=0)
    except Exception as e:
        print(f"migrate failed: {e}")
    try:
        call_command("collectstatic", "--noinput", "--clear", verbosity=0)
    except Exception as e:
        print(f"collectstatic failed: {e}")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
