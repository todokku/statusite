web: newrelic-admin run-program gunicorn config.wsgi:application
worker: newrelic-admin run-program honcho start -f Procfile_honcho
release: newrelic-admin run-program python manage.py migrate
