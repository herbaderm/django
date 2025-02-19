#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo "🔄 Starting build process..."

# Environment variable'ları ayarla
export DJANGO_SETTINGS_MODULE=myproject.settings
export PYTHONPATH=/opt/render/project/src

# Python sürümünü kontrol et
python --version

# Virtual environment'ı temizle ve yeniden oluştur
echo "🧹 Cleaning virtual environment..."
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# Pip'i güncelle
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Requirements'ları yükle
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Django'yu kontrol et
echo "🔍 Checking Django installation..."
python -c "import django; print(django.get_version())"

# Collect static
echo "📚 Collecting static files..."
python manage.py collectstatic --noinput

# Migrations
echo "🔄 Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Superuser oluştur
echo "👤 Creating superuser..."
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-adminpassword}"
python manage.py createsuperuser --noinput || true

echo "✅ Build process completed!"