#!/bin/bash

set -e

echo "🔹 Stopping existing containers..."

# python manage.py migrate &&
# echo "🔹 Migrations done..."

python manage.py collectstatic --noinput &&
echo "🔹 Static files collected..."

gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 2   &&
echo "🔹 Starting gunicorn..."