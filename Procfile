release: python manage.py migrate && python manage.py create_superuser
web: gunicorn marketplace_backend.wsgi:application
