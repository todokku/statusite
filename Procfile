release: newrelic-admin runprogram python manage.py migrate
web: newrelic-admin runprogram gunicorn config.wsgi:application
worker: newrelic-admin runprogram honcho start -f Procfile_honcho
