#!/bin/sh
set -e

echo "Starting project setup..."

echo "Applying database migrations..."
python manage.py makemigrations --merge
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn djangopayment.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 200 \
  --log-level info