#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput

# Create superuser
python manage.py createsuperuser --noinput || true