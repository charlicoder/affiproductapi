#!/bin/bash

set -e  # Exit on any error

# CONFIGURE THESE PATHS
PROJECT_DIR="/home/ubuntu/affiproductapi"
VENV_DIR="$PROJECT_DIR/venv"
GUNICORN_SERVICE="affiproductapi"  # Your gunicorn systemd service name

echo ">>> Updating codebase"
cd "$PROJECT_DIR"
git pull origin main  # or your branch name

echo ">>> Activating virtual environment"
source "$VENV_DIR/bin/activate"

echo ">>> Installing dependencies (optional)"
pip install -r requirements.txt

# echo ">>> Running Django migrations"
# python manage.py migrate --noinput

echo ">>> Collecting static files"
python manage.py collectstatic --noinput

echo ">>> Restarting Gunicorn and Nginx"
sudo systemctl restart "$GUNICORN_SERVICE"
sudo systemctl restart nginx

echo ">>> Deployment complete!"
