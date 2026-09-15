import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

import django
from django.core.management import call_command


django.setup()
call_command("migrate", run_syncdb=True, verbosity=0, interactive=False)

from crm.wsgi import application

app = application
