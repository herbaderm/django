#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Debug için
echo "Starting build.sh script..."

# Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Build script completed."