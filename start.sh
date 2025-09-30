#!/bin/bash
# Startup script for Render deployment

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py create_superuser

# Start the application
exec gunicorn marketplace_backend.wsgi:application
