#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Make migrations for tracker app
python manage.py makemigrations tracker

# Make migrations for all apps
python manage.py makemigrations

# Apply all migrations
python manage.py migrate