"""
WSGI config for smart9adhya project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart9adhya.settings')
application = get_wsgi_application()
