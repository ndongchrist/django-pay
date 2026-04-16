#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting project setup..."

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Applying database migrations..."
python manage.py makemigrations --merge
python manage.py migrate --noinput


echo "Collecting static files..."
python manage.py collectstatic --noinput


echo "Starting Gunicorn server..."
# Customize worker count and timeout as needed
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 200 \
  --log-level info
