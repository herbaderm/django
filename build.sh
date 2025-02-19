#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo "🔄 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📚 Collecting static files..."
python manage.py collectstatic --noinput

# Clean migrations
echo "🧹 Cleaning migrations..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Make and run migrations
echo "🔄 Creating and applying migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput --verbosity 2

# Create superuser
echo "👤 Creating superuser..."
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-adminpassword}"
python manage.py createsuperuser --noinput || true

echo "✅ Build process completed!"