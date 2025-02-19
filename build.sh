#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

echo "Build script completed."