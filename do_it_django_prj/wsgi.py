"""
WSGI config for do_it_django_prj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

django.setup()

from django.core.management import call_command
call_command('migrate')  # 마이그레이션 자동 수행

application = get_wsgi_application()